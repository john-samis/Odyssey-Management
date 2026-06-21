# Operations guide

## 1. Create the permanent attendance source

Use the dedicated regular Google account to own one permanent Google Form and the Sheet that receives its responses.

- Keep the existing questions and column order: `Timestamp`, verified Google `Email Address`, `First Name`, `Last Name`, and optional alternate email address.
- Configure the Form to collect verified email addresses.
- Link responses to a single Google Sheet. Do not create a new Sheet each week.
- Set the Sheet's timezone to **America/Toronto**. The job reads Google Sheets serial timestamps as that local timezone.
- Update `src/cloudflare/pages/_redirects` so `/form` points to the permanent Form responder URL, then deploy the Pages files once. No future weekly redirect update is required.

## 2. Configure Google Cloud access

Use one GCP project for the Cloud Run Job, Gmail API OAuth client, Secret Manager, and Cloud Scheduler.

Enable these APIs:

- Cloud Run Admin API
- Cloud Scheduler API
- Secret Manager API
- Cloud Build API
- Artifact Registry API
- Google Sheets API
- Gmail API

Create two service accounts:

| Account | Purpose | Required access |
| --- | --- | --- |
| Cloud Run runtime account | Reads the attendance Sheet and accesses secrets | Share the response Sheet with this account as a Viewer; grant `roles/secretmanager.secretAccessor` for the two secrets. |
| Cloud Scheduler invoker | Starts the weekly Cloud Run Job | Grant the least privilege that permits running this specific job (normally `roles/run.developer` for the job/project). |

The runtime service account is a GCP identity. It is not the Gmail sender. The dedicated regular Google account remains the Form/Sheet owner and Gmail sender.

## 3. Authorize Gmail once

Create an OAuth desktop client in the same GCP project and enable the Gmail API. Sign in as the dedicated regular Google account when running this helper on a trusted workstation:

```powershell
python scripts/authorize_gmail.py `
  --client-secrets C:\secure\google-oauth-client.json `
  --output C:\secure\gmail-oauth-token.json
```

The output contains a refresh token and must never be committed. Store its full JSON content in Google Secret Manager as `odyssey-gmail-oauth-token`.

The job requests only the Gmail `send` scope. If the OAuth consent screen is left in testing mode, refresh-token lifetime and permitted users are constrained; configure the consent screen appropriately for the dedicated sender account before relying on the scheduled job.

## 4. Create the runtime configuration secret

Store the following JSON as `odyssey-attendance-config` in Secret Manager. Replace example values with the permanent Sheet ID, sheet tab name, sender, and organizer recipients.

```json
{
  "spreadsheet_id": "google-sheet-id",
  "sheet_name": "Form Responses 1",
  "recipients": [
    "organizer@example.com",
    "backup-organizer@example.com"
  ],
  "sender_email": "dedicated-attendance-account@example.com",
  "timezone": "America/Toronto",
  "session_start": "18:30",
  "session_end": "22:00",
  "timestamp_header": "Timestamp"
}
```

`recipients` may contain one address or many. All recipients receive one email and are visible in its `To` header.

For local development only, set `ATTENDANCE_CONFIG_JSON` and `GMAIL_OAUTH_TOKEN_JSON` in an ignored `.env` file. Cloud Run injects both from Secret Manager.

## 5. Build and deploy the Cloud Run Job

The GitHub deployment workflow expects repository variables for the GCP project, region, Artifact Registry repository, Workload Identity Provider, deployer service account, Cloud Run runtime service account, and the two secret names. Its deployer identity needs permission to build/push the image, update the Cloud Run Job, and impersonate the runtime account.

The deployed job has no HTTP endpoint. It receives the two secrets as environment variables, runs once, and exits. Automatic Cloud Run task retries are disabled so a transient failure is visible instead of silently producing duplicate mail. Configure Cloud Monitoring alerting for failed job executions.

Before enabling the weekly scheduler, trigger one manual job execution with a known historical date and verify:

- the selected rows are exactly the expected submissions;
- the workbook headers and rows match the Sheet;
- the dedicated sender account is used;
- every configured organizer receives the report;
- the empty-report alert is understandable.

## 6. Schedule the weekly job

Create an HTTP Cloud Scheduler job that calls the Cloud Run Jobs `:run` API. Use the scheduler invoker service account and OAuth scope `https://www.googleapis.com/auth/cloud-platform`.

```bash
gcloud scheduler jobs create http odyssey-attendance-weekly \
  --location=REGION \
  --schedule="0 22 * * 2" \
  --time-zone="America/Toronto" \
  --uri="https://run.googleapis.com/v2/projects/PROJECT_ID/locations/REGION/jobs/odyssey-attendance:run" \
  --http-method=POST \
  --oauth-service-account-email=SCHEDULER_SERVICE_ACCOUNT \
  --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
```

Replace `PROJECT_ID`, `REGION`, and `SCHEDULER_SERVICE_ACCOUNT`. Confirm the exact Cloud Run Jobs URI generated for your project before enabling it. The schedule means every Tuesday at 10:00 PM Toronto time, including daylight-saving transitions.

## Expected behavior

- A report includes every form response whose timestamp is in `[18:30, 22:00)` local time for that Tuesday. It intentionally does not deduplicate submissions.
- A no-response evening still produces an attached empty XLSX and an `ALERT: no responses` email.
- There is no supported correction or resend workflow. The report sent at 10:00 PM is the weekly delivery record.
- Job failures must be handled through Cloud Monitoring and a deliberate manual operational response; do not modify the Form or redirect weekly.
