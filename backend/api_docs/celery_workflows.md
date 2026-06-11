# Celery Workflows

## Purpose

Documents delayed care request automation handled by Celery workers.

## Workflow URLs

No public API endpoint. Workflows are scheduled internally when a nurse accepts a care request.

## Authentication

Not user-facing. Tasks execute as system workflows.

## Permissions

System-only.

## Scheduled Tasks

### 30 Minute Journey Warning

Task:

`apps.requests.tasks.send_journey_warning_task`

Trigger:

Scheduled after request acceptance with a 30 minute countdown.

Behavior:

- If the request is still `ACCEPTED` or `PREPARING`
- And an assigned nurse exists
- And `journey_started_at` is still empty
- Persist one `JOB_WARNING` notification for the assigned nurse
- Persist an audit log with action `CARE_REQUEST_JOURNEY_WARNING_SENT`

Idempotency:

- If the warning already exists for the care request, the task returns `skipped`.
- If the journey has already started, the task returns `skipped`.

### 60 Minute Assignment Cancellation

Task:

`apps.requests.tasks.cancel_stalled_assignment_task`

Trigger:

Scheduled after request acceptance with a 60 minute countdown.

Behavior:

- If the request is still `ACCEPTED` or `PREPARING`
- And an assigned nurse exists
- And `journey_started_at` is still empty
- Remove the assigned nurse
- Return the request to `PENDING`
- Mark accepted offer as `CANCELLED`
- Return the nurse to `ONLINE`
- Increment nurse cancellation count
- Persist a `JOB_CANCELLED` notification for the patient
- Persist an audit log with action `CARE_REQUEST_ASSIGNMENT_AUTO_CANCELLED`
- Call matching again so the request returns to the matching pool

Idempotency:

- If the journey has already started, the task returns `skipped`.
- If the assignment was already removed, the task returns `skipped`.
- Repeated task execution does not cancel active journeys or completed visits.

## Monitoring Hooks

Every workflow returns a structured payload:

```json
{
  "action": "journey_warning",
  "care_request_id": 42,
  "status": "sent",
  "details": {
    "notification_id": 100
  }
}
```

Supported statuses:

- `sent`
- `requeued`
- `skipped`
- `missing`

The workflow service also writes structured log messages:

- `care_request_workflow_result`
- `care_request_journey_warning_sent`
- `care_request_assignment_auto_cancelled`

## Retry Strategy

Both tasks use Celery autoretry for transient database failures:

- `autoretry_for = (OperationalError,)`
- `retry_backoff = true`
- `retry_jitter = true`
- `max_retries = 3`

## Business Rules

- Workflow tasks never expose medical information in notification payloads.
- Warning notifications go to the assigned nurse.
- Automatic assignment cancellation notifications go to the patient.
- Assignment cancellation does not hard-delete records.
- Assignment cancellation returns the request to matching without broadcasting to all nurses.
- Matching still respects nurse eligibility, specialization, travel radius, and bounded notification rules.
