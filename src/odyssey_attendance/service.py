"""Orchestration of reading, selecting, rendering, and sending attendance reports."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from .config import Settings
from .models import AttendanceReport
from .time_windows import build_window, select_attendance_rows
from .workbook import render_workbook

LOGGER = logging.getLogger(__name__)


class AttendanceReader(Protocol):
    def read_rows(self) -> Sequence[Sequence[object]]: ...


class AttendanceSender(Protocol):
    def send_report(self, report: AttendanceReport, workbook: bytes) -> str: ...


@dataclass
class AttendanceReportService:
    settings: Settings
    reader: AttendanceReader
    sender: AttendanceSender

    def run(self, session_date: date) -> str:
        window = build_window(
            session_date,
            self.settings.session_start,
            self.settings.session_end,
            self.settings.timezone,
        )
        report = select_attendance_rows(
            self.reader.read_rows(),
            window,
            self.settings.timestamp_header,
            self.settings.timezone,
        )
        workbook = render_workbook(report)
        message_id = self.sender.send_report(report, workbook)
        LOGGER.info(
            "attendance_report_sent session_date=%s attendee_count=%s message_id=%s",
            session_date.isoformat(),
            report.attendee_count,
            message_id,
        )
        return message_id
