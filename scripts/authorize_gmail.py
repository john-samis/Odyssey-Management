"""Create a Gmail OAuth refresh-token file for the dedicated attendance account.

Run this manually on a trusted workstation. It must never run in Cloud Run or CI.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorize the dedicated Gmail sender for Odyssey attendance")
    parser.add_argument("--client-secrets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite existing token file: {args.output}")

    flow = InstalledAppFlow.from_client_secrets_file(str(args.client_secrets), [GMAIL_SEND_SCOPE])
    credentials = flow.run_local_server(port=0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(credentials.to_json(), encoding="utf-8")
    print(f"Wrote Gmail OAuth token to {args.output}")


if __name__ == "__main__":
    main()
