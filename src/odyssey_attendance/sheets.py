"""Google Sheets response reader."""

from __future__ import annotations

from collections.abc import Sequence

import google.auth
from googleapiclient.discovery import build

from .config import Settings

SHEETS_READONLY_SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"


class GoogleSheetsReader:
    """Read unformatted Google Form response values using the Cloud Run service account."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def read_rows(self) -> Sequence[Sequence[object]]:
        credentials, _ = google.auth.default(scopes=[SHEETS_READONLY_SCOPE])
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        range_name = f"'{self._settings.sheet_name}'!A:ZZ"
        response = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self._settings.spreadsheet_id,
                range=range_name,
                valueRenderOption="UNFORMATTED_VALUE",
                dateTimeRenderOption="SERIAL_NUMBER",
            )
            .execute()
        )
        return response.get("values", [])
