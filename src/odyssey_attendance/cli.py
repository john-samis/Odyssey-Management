"""CLI entry point used by the Cloud Run Job."""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime

from .config import Settings
from .gmail import GmailSender
from .service import AttendanceReportService
from .sheets import GoogleSheetsReader


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and email an Odyssey attendance workbook")
    parser.add_argument(
        "--session-date",
        type=date.fromisoformat,
        help="Local session date in YYYY-MM-DD format. Defaults to today's configured local date.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = Settings.from_environment()
    session_date = args.session_date or datetime.now(settings.timezone).date()
    service = AttendanceReportService(settings, GoogleSheetsReader(settings), GmailSender(settings))
    service.run(session_date)


if __name__ == "__main__":
    main()
