from datetime import date, time
from zoneinfo import ZoneInfo

from odyssey_attendance.config import Settings
from odyssey_attendance.gmail import _build_message
from odyssey_attendance.models import AttendanceReport
from odyssey_attendance.time_windows import build_window


def _settings() -> Settings:
    return Settings(
        spreadsheet_id="spreadsheet-id",
        sheet_name="Form Responses 1",
        recipients=("organizer@example.com", "backup@example.com"),
        sender_email="attendance@example.com",
        timezone_name="America/Toronto",
        session_start=time(18, 30),
        session_end=time(22, 0),
        gmail_oauth_token_json='{"refresh_token": "test"}',
    )


def test_empty_report_email_is_an_alert_with_an_attachment() -> None:
    timezone = ZoneInfo("America/Toronto")
    report = AttendanceReport(
        headers=("Timestamp", "Email Address"),
        rows=(),
        window=build_window(date(2026, 6, 2), time(18, 30), time(22, 0), timezone),
    )

    message = _build_message(_settings(), report, b"workbook")

    assert "ALERT: no responses" in message["Subject"]
    assert message["To"] == "organizer@example.com, backup@example.com"
    assert "This may mean nobody attended" in message.get_body().get_content()
    assert message.get_payload()[-1].get_filename() == "odyssey-attendance-2026-06-02.xlsx"
