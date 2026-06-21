"""Timestamp conversion and attendance-window selection."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo

from .models import AttendanceReport, AttendanceWindow


class AttendanceDataError(ValueError):
    """Raised when the response sheet does not match the agreed attendance schema."""


def build_window(session_date: date, session_start: time, session_end: time, timezone: ZoneInfo) -> AttendanceWindow:
    return AttendanceWindow(
        session_date=session_date,
        starts_at=datetime.combine(session_date, session_start, tzinfo=timezone),
        ends_at=datetime.combine(session_date, session_end, tzinfo=timezone),
    )


def select_attendance_rows(
    values: Iterable[Iterable[object]],
    window: AttendanceWindow,
    timestamp_header: str,
    timezone: ZoneInfo,
) -> AttendanceReport:
    """Retain each source response whose timestamp is within the local attendance window."""

    all_rows = [tuple(row) for row in values]
    if not all_rows:
        raise AttendanceDataError("The response sheet has no header row")

    headers = tuple(str(value).strip() for value in all_rows[0])
    if not headers:
        raise AttendanceDataError("The response sheet has an empty header row")

    try:
        timestamp_index = next(
            index for index, header in enumerate(headers) if header.casefold() == timestamp_header.strip().casefold()
        )
    except StopIteration as exc:
        raise AttendanceDataError(f"The response sheet is missing the {timestamp_header!r} column") from exc

    selected: list[tuple[object, ...]] = []
    for raw_row in all_rows[1:]:
        row = raw_row + ("",) * (len(headers) - len(raw_row))
        if len(row) > len(headers):
            row = row[: len(headers)]
        timestamp = _as_local_datetime(row[timestamp_index], timezone)
        if window.starts_at <= timestamp < window.ends_at:
            # Keep the response's other cells unchanged, but render the Sheet serial timestamp as a normal Excel date.
            # Excel cells are intentionally timezone-naive; the local time has already been resolved using the Sheet timezone.
            rendered_row = list(row)
            rendered_row[timestamp_index] = timestamp.replace(tzinfo=None)
            selected.append(tuple(rendered_row))

    return AttendanceReport(headers=headers, rows=tuple(selected), window=window)


def _as_local_datetime(value: object, timezone: ZoneInfo) -> datetime:
    if isinstance(value, bool):
        raise AttendanceDataError("A timestamp value cannot be boolean")
    if isinstance(value, (int, float)):
        # Google Sheets serial date zero is 1899-12-30. The serial is in the spreadsheet's local timezone.
        naive = datetime(1899, 12, 30) + timedelta(days=float(value))
        return naive.replace(tzinfo=timezone)
    if isinstance(value, datetime):
        return value.astimezone(timezone) if value.tzinfo else value.replace(tzinfo=timezone)
    if isinstance(value, str):
        return _parse_timestamp_string(value, timezone)
    raise AttendanceDataError(f"Unsupported timestamp value: {value!r}")


def _parse_timestamp_string(value: str, timezone: ZoneInfo) -> datetime:
    cleaned = value.strip()
    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt).replace(tzinfo=timezone)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError as exc:
        raise AttendanceDataError(f"Could not parse timestamp {value!r}") from exc
    return parsed.astimezone(timezone) if parsed.tzinfo else parsed.replace(tzinfo=timezone)
