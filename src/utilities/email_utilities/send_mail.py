"""
Send an email 'main' loop
"""
from pathlib import Path
from src.utilities.app_logger import AppLogger
from src.utilities.email_utilities.smtp_client import EmailClient, EmailMessage, SMTPEmailException
from src.utilities.email_utilities.email_templates import HTMLEmailTemplate


def main() -> None:
    ATTACHMENT_PATH: Path = Path("attendance_jan06.xlsx")
    recipients: list[str] = [
        "jsamis311@gmail.com",
        "sokos.greg@gmail.com",
        "odysseydancetroupe@helleniccommunity.com"
        ]

    for email_addr in recipients:
        mail_template: EmailMessage = EmailMessage(
            destination_email_address=email_addr,
            subject="[Odyssey Management] Today's Attendance",
            plain_text_body="Fall Back to Text [ERROR]",
            html_body=HTMLEmailTemplate.ATTENDANCE_AUTOMATED_SEND_HTML,
            attachments=[ATTACHMENT_PATH],
        )

        try:
            email_client = EmailClient()

            print(f"Sending Email to {email_addr}...")
            if not email_client.send_email(mail_template):
                print(f"Email to {email_addr} FAIL")
            else:
                print(f"Email to {email_addr} PASS")
        except SMTPEmailException as e:
            print(f"Error with Email Transfer {type(e)}: {e}")
        except Exception as e:
            print(f"Error with Email Transfer {type(e)}: {e}")



if __name__ == '__main__':
    main()





