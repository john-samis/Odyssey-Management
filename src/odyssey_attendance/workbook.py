"""XLSX rendering for a selected attendance report."""

from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font

from .models import AttendanceReport

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def render_workbook(report: AttendanceReport) -> bytes:
    """Render the original form columns and selected response rows to an XLSX workbook."""

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    sheet.append(report.headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:{_column_name(len(report.headers))}{max(1, report.attendee_count + 1)}"

    for row in report.rows:
        sheet.append(row)

    for column_index, header in enumerate(report.headers, start=1):
        if header.casefold() == "timestamp":
            for row_index in range(2, report.attendee_count + 2):
                sheet.cell(row=row_index, column=column_index).number_format = "m/d/yyyy h:mm:ss"

    for index, header in enumerate(report.headers, start=1):
        longest = max([len(str(header)), *(len(str(row[index - 1])) for row in report.rows)], default=10)
        sheet.column_dimensions[_column_name(index)].width = min(max(longest + 2, 12), 60)

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def filename_for(report: AttendanceReport) -> str:
    return f"odyssey-attendance-{report.window.session_date.isoformat()}.xlsx"


def _column_name(index: int) -> str:
    """Return an Excel column name for a positive one-based column index."""

    if index < 1:
        raise ValueError("Excel column index must be positive")
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result
