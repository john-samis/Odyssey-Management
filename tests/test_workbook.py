from datetime import date, datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from openpyxl import load_workbook

from odyssey_attendance.models import AttendanceReport, AttendanceWindow
from odyssey_attendance.workbook import filename_for, render_workbook


def test_render_workbook_preserves_headers_and_rows() -> None:
    timezone = ZoneInfo("America/Toronto")
    report = AttendanceReport(
        headers=("Timestamp", "Email Address", "First Name"),
        rows=((datetime(2026, 6, 2, 19, 10, 21), "member@example.com", "Member"),),
        window=AttendanceWindow(
            session_date=date(2026, 6, 2),
            starts_at=datetime(2026, 6, 2, 18, 30, tzinfo=timezone),
            ends_at=datetime(2026, 6, 2, 22, 0, tzinfo=timezone),
        ),
    )

    workbook = load_workbook(BytesIO(render_workbook(report)))
    sheet = workbook["Attendance"]

    assert tuple(cell.value for cell in sheet[1]) == report.headers
    assert tuple(cell.value for cell in sheet[2]) == report.rows[0]
    assert sheet["A2"].number_format == "m/d/yyyy h:mm:ss"
    assert filename_for(report) == "odyssey-attendance-2026-06-02.xlsx"
