"""Domain models shared by the scheduled attendance-report job."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class AttendanceWindow:
    """The inclusive/exclusive local-time window used to select form responses."""

    session_date: date
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class AttendanceReport:
    """A workbook-ready attendance report for a single practice."""

    headers: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    window: AttendanceWindow

    @property
    def attendee_count(self) -> int:
        return len(self.rows)
