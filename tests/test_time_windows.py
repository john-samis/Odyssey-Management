from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from odyssey_attendance.time_windows import AttendanceDataError, build_window, select_attendance_rows

TORONTO = ZoneInfo("America/Toronto")
HEADERS = ("Timestamp", "Email Address", "First Name", "Last Name", "Email Address if Different")


def _google_serial(value: datetime) -> float:
    return (value - datetime(1899, 12, 30)).total_seconds() / 86_400


def test_select_attendance_rows_includes_start_and_excludes_end() -> None:
    window = build_window(date(2026, 6, 2), time(18, 30), time(22, 0), TORONTO)
    values = [
        HEADERS,
        (_google_serial(datetime(2026, 6, 2, 18, 29, 59)), "before@example.com", "Before", "Start", ""),
        (_google_serial(datetime(2026, 6, 2, 18, 30)), "start@example.com", "Start", "Included", ""),
        (_google_serial(datetime(2026, 6, 2, 21, 59, 59)), "late@example.com", "Late", "Included", ""),
        (_google_serial(datetime(2026, 6, 2, 22, 0)), "end@example.com", "End", "Excluded", ""),
    ]

    report = select_attendance_rows(values, window, "Timestamp", TORONTO)

    assert report.headers == HEADERS
    assert [row[1] for row in report.rows] == ["start@example.com", "late@example.com"]
    assert report.rows[0][0] == datetime(2026, 6, 2, 18, 30)


def test_select_attendance_rows_accepts_the_existing_timestamp_format() -> None:
    window = build_window(date(2026, 6, 2), time(18, 30), time(22, 0), TORONTO)
    values = [HEADERS, ("6/2/2026 19:10:21", "member@example.com", "A", "Member", "")]

    report = select_attendance_rows(values, window, "Timestamp", TORONTO)

    assert report.attendee_count == 1


def test_select_attendance_rows_requires_timestamp_header() -> None:
    window = build_window(date(2026, 6, 2), time(18, 30), time(22, 0), TORONTO)

    with pytest.raises(AttendanceDataError, match="Timestamp"):
        select_attendance_rows([("Email Address",)], window, "Timestamp", TORONTO)
