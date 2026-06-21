"""Configuration parsing for the attendance-report job."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import time
from email.utils import parseaddr
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class ConfigurationError(ValueError):
    """Raised when required job configuration is missing or malformed."""


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{key} must be a non-empty string")
    return value.strip()


def _parse_recipients(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        candidates = value.split(",")
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        candidates = value
    else:
        raise ConfigurationError("recipients must be a comma-separated string or a list of email addresses")

    recipients: list[str] = []
    for candidate in candidates:
        address = parseaddr(candidate.strip())[1]
        if not address or "@" not in address:
            raise ConfigurationError(f"Invalid recipient email address: {candidate!r}")
        recipients.append(address)

    if not recipients:
        raise ConfigurationError("At least one recipient is required")
    return tuple(recipients)


def _parse_time(value: str, field_name: str) -> time:
    try:
        parsed = time.fromisoformat(value)
    except ValueError as exc:
        raise ConfigurationError(f"{field_name} must use HH:MM or HH:MM:SS format") from exc
    if parsed.tzinfo is not None:
        raise ConfigurationError(f"{field_name} must be a local time without a timezone")
    return parsed


@dataclass(frozen=True)
class Settings:
    """Runtime settings supplied through a secret-backed JSON environment variable."""

    spreadsheet_id: str
    sheet_name: str
    recipients: tuple[str, ...]
    sender_email: str
    timezone_name: str
    session_start: time
    session_end: time
    gmail_oauth_token_json: str
    timestamp_header: str = "Timestamp"

    @property
    def timezone(self) -> ZoneInfo:
        try:
            return ZoneInfo(self.timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ConfigurationError(f"Unknown IANA timezone: {self.timezone_name}") from exc

    @classmethod
    def from_environment(cls) -> "Settings":
        config_json = os.getenv("ATTENDANCE_CONFIG_JSON", "")
        if not config_json:
            raise ConfigurationError("ATTENDANCE_CONFIG_JSON is required")

        try:
            config = json.loads(config_json)
        except json.JSONDecodeError as exc:
            raise ConfigurationError("ATTENDANCE_CONFIG_JSON must be valid JSON") from exc
        if not isinstance(config, dict):
            raise ConfigurationError("ATTENDANCE_CONFIG_JSON must be a JSON object")

        token_json = _read_gmail_token()
        sender = _required_string(config, "sender_email")
        sender_address = parseaddr(sender)[1]
        if not sender_address or "@" not in sender_address:
            raise ConfigurationError("sender_email must be a valid email address")

        settings = cls(
            spreadsheet_id=_required_string(config, "spreadsheet_id"),
            sheet_name=_required_string(config, "sheet_name"),
            recipients=_parse_recipients(config.get("recipients")),
            sender_email=sender_address,
            timezone_name=_required_string(config, "timezone"),
            session_start=_parse_time(_required_string(config, "session_start"), "session_start"),
            session_end=_parse_time(_required_string(config, "session_end"), "session_end"),
            gmail_oauth_token_json=token_json,
            timestamp_header=str(config.get("timestamp_header", "Timestamp")).strip() or "Timestamp",
        )
        if settings.session_start >= settings.session_end:
            raise ConfigurationError("session_start must be earlier than session_end")
        _ = settings.timezone
        return settings


def _read_gmail_token() -> str:
    inline = os.getenv("GMAIL_OAUTH_TOKEN_JSON", "").strip()
    token_file = os.getenv("GMAIL_OAUTH_TOKEN_FILE", "").strip()
    if bool(inline) == bool(token_file):
        raise ConfigurationError("Set exactly one of GMAIL_OAUTH_TOKEN_JSON or GMAIL_OAUTH_TOKEN_FILE")

    token_json = Path(token_file).read_text(encoding="utf-8") if token_file else inline
    try:
        parsed = json.loads(token_json)
    except json.JSONDecodeError as exc:
        raise ConfigurationError("Gmail OAuth token must be valid JSON") from exc
    if not isinstance(parsed, dict) or not parsed.get("refresh_token"):
        raise ConfigurationError("Gmail OAuth token must contain a refresh_token")
    return token_json
