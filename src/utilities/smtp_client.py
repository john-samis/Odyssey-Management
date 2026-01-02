"""
Module using the built-in smtp and email libraries to send automated
emails over gmail smtp. Using Google Mail as a smtp server with
pre-authorized credentials. Encryption via SSL


"""
import os
import smtplib
import ssl
from enum import StrEnum
from email.message import Message
from dataclasses import dataclass, field


class SMTPEmailException(Exception):
    """ Custom Exception for this Module """


class SMTPServerConfig(StrEnum):
    SMTP_SERVER= "smtp.gmail.com"
    SMTP_PORT= "465"
    SECURITY_CONTRACT = "SSL"  # Secure Sockets Layer


@dataclass
class SMTPConfig:
    sender_email_address: str
    google_smtp_app_passwd: str
    smtp_server: str = field(default=SMTPServerConfig.SMTP_SERVER)
    smtp_port: str = field(default=SMTPServerConfig.SMTP_PORT)
    security_contract: str = field(default=SMTPServerConfig.SECURITY_CONTRACT)


class SMTPClient:
    """
    SMTP Client from smtplib.
    Composed of SMTPConfig and related defaults.

    """
    # The service account for the Odyssey Management Software, stored via ENV VARS
    _SENDER_EMAIL_ADDRESS: str = "SENDER_EMAIL_ADDRESS"
    _GOOGLE_SMTP_APP_PASS: str = "GOOGLE_SMTP_APP_PASS"


    def __init__(self) -> None:
        self.cfg: SMTPConfig = SMTPConfig(
            sender_email_address=os.getenv(self._SENDER_EMAIL_ADDRESS, ""),
            google_smtp_app_passwd=os.getenv(self._GOOGLE_SMTP_APP_PASS, ""),
        )


@dataclass
class PlainTextEmailMessage:
    header: str
    body: str



class EmailSender:
    """ High-level"""

