# Odyssey attendance management

This repository produces and emails the weekly Odyssey dance attendance workbook.

## Production flow

1. Members complete one permanent Google Form. Its responses are written to one permanent Google Sheet.
2. Cloud Scheduler starts a Cloud Run Job every Tuesday at 10:00 PM in `America/Toronto`.
3. The job selects all responses submitted from 6:30 PM through 10:00 PM local time, creates an XLSX file with the source columns intact, and emails it to the configured organizer recipients.
4. If there are no submissions, the job sends an empty workbook and an explicit alert in the email body.

The Cloudflare Pages site is deliberately separate. Its only job is to redirect `/form` to the permanent Google Form. It does not authenticate attendance or call the Cloud Run job.

## Local development

Python 3.12 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
```

The job reads its configuration from `ATTENDANCE_CONFIG_JSON` and Gmail credentials from `GMAIL_OAUTH_TOKEN_JSON`. Both are injected from Google Secret Manager in Cloud Run. See [docs/OPERATIONS.md](docs/OPERATIONS.md) for the expected values, one-time Gmail authorization, and deployment setup.

For a local dry run, supply those variables in an ignored `.env` file and invoke:

```powershell
odyssey-attendance-report --session-date 2026-06-02
```

## Repository layout

- `src/odyssey_attendance/` — the Cloud Run Job application
- `tests/` — unit tests with no live Google calls
- `scripts/authorize_gmail.py` — one-time OAuth helper for the dedicated Gmail account
- `docs/OPERATIONS.md` — cloud setup and weekly operational behavior
- `src/cloudflare/pages/` — static Cloudflare Pages redirect assets
