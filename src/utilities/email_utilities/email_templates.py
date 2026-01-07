"""
Store the prebuilt HTML email templates for automated use

"""

from enum import StrEnum, Enum
from src.utilities.email_utilities.smtp_client import EmailMessage

class HTMLEmailTemplate(StrEnum):
    ATTENDANCE_AUTOMATED_SEND_HTML = """\
    <html>
      <body>
        <p>Hey guys,<br>
        <br>
        Please see attached for today's attendance sheet.<br>
        <p>This is an Automated Email Sent from the Odyssey Management Software.</p>
      </body>
    </html>
    """



