from datetime import date, time
from zoneinfo import ZoneInfo

from odyssey_attendance.config import Settings
from odyssey_attendance.models import AttendanceReport
from odyssey_attendance.service import AttendanceReportService


class FakeReader:
    def read_rows(self) -> list[list[object]]:
        return [["Timestamp", "Email Address", "First Name"], [46175.8, "member@example.com", "Member"]]


class FakeSender:
    report: AttendanceReport | None = None
    workbook: bytes | None = None

    def send_report(self, report: AttendanceReport, workbook: bytes) -> str:
        self.report = report
        self.workbook = workbook
        return "gmail-message-id"


def test_service_reads_renders_and_sends_selected_attendance() -> None:
    settings = Settings(
        spreadsheet_id="spreadsheet-id",
        sheet_name="Form Responses 1",
        recipients=("organizer@example.com", "backup@example.com"),
        sender_email="attendance@example.com",
        timezone_name="America/Toronto",
        session_start=time(18, 30),
        session_end=time(22, 0),
        gmail_oauth_token_json='{"refresh_token": "test"}',
    )
    sender = FakeSender()
    service = AttendanceReportService(settings, FakeReader(), sender)

    message_id = service.run(date(2026, 6, 2))

    assert message_id == "gmail-message-id"
    assert sender.report is not None
    assert sender.report.attendee_count == 1
    assert sender.workbook is not None
    assert len(sender.workbook) > 100
    assert settings.timezone == ZoneInfo("America/Toronto")
