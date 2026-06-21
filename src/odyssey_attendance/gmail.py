"""Gmail API delivery for attendance workbooks."""

from __future__ import annotations

import base64
import json
from datetime import date, datetime
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .config import Settings
from .models import AttendanceReport
from .workbook import XLSX_CONTENT_TYPE, filename_for

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


class GmailSender:
    """Send reports through the dedicated Google account's Gmail API authorization."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send_report(self, report: AttendanceReport, workbook: bytes) -> str:
        message = _build_message(self._settings, report, workbook)
        token_info = json.loads(self._settings.gmail_oauth_token_json)
        credentials = Credentials.from_authorized_user_info(token_info, scopes=[GMAIL_SEND_SCOPE])
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        response = service.users().messages().send(userId="me", body={"raw": encoded}).execute()
        return str(response["id"])


def _build_message(settings: Settings, report: AttendanceReport, workbook: bytes) -> EmailMessage:
    session_label = _format_date(report.window.session_date)
    window_start = _format_local_time(report.window.starts_at)
    window_end = _format_local_time(report.window.ends_at)
    if report.attendee_count:
        subject = f"[Odyssey Attendance] {session_label} ({report.attendee_count} responses)"
        body = (
            f"The attendance workbook for {session_label} is attached.\n\n"
            f"It contains {report.attendee_count} form response(s) submitted between "
            f"{window_start} and {window_end} "
            f"{report.window.starts_at.tzname()}."
        )
    else:
        subject = f"[Odyssey Attendance] ALERT: no responses for {session_label}"
        body = (
            f"No attendance form responses were recorded between {window_start} and "
            f"{window_end} {report.window.starts_at.tzname()} on {session_label}.\n\n"
            "This may mean nobody attended, the form was not used, or the intake system needs review. "
            "An empty attendance workbook is attached."
        )

    message = EmailMessage()
    message["From"] = settings.sender_email
    message["To"] = ", ".join(settings.recipients)
    message["Subject"] = subject
    message.set_content(body)

    maintype, subtype = XLSX_CONTENT_TYPE.split("/", 1)
    message.add_attachment(workbook, maintype=maintype, subtype=subtype, filename=filename_for(report))
    return message


def _format_date(value: date) -> str:
    return f"{value.strftime('%A, %B')} {value.day}, {value.year}"


def _format_local_time(value: datetime) -> str:
    hour = value.hour % 12 or 12
    suffix = "AM" if value.hour < 12 else "PM"
    return f"{hour}:{value.minute:02d} {suffix}"
