# Create Visit Notes

## Purpose

Create protected clinical documentation for an in-progress home-care visit.

## Endpoint URL

`/api/visit-notes/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Only the nurse assigned to the care request may create visit notes.

## Request Schema

```json
{
  "care_request_id": 42,
  "vitals": "BP 120/80, pulse 78",
  "observations": "Patient stable",
  "medication_given": "Paracetamol 500mg",
  "recommendations": "Hydration and rest",
  "follow_up_required": true,
  "follow_up_schedule": "3_DAYS"
}
```

Supported `follow_up_schedule` values:

- `1_DAY`
- `3_DAYS`
- `1_WEEK`
- `2_WEEKS`
- `1_MONTH`

## Response Schema

```json
{
  "id": 10,
  "care_request_id": 42,
  "patient_id": 7,
  "nurse_id": 3,
  "nurse_name": "Jane Wanjiku",
  "vitals": "BP 120/80, pulse 78",
  "observations": "Patient stable",
  "medication_given": "Paracetamol 500mg",
  "recommendations": "Hydration and rest",
  "follow_up_required": true,
  "follow_up_schedule": "3_DAYS",
  "follow_up_due_at": "2026-06-14T10:00:00Z",
  "created_at": "2026-06-11T10:00:00Z",
  "updated_at": "2026-06-11T10:00:00Z"
}
```

## Error Responses

- `400` when the request is not in progress, follow-up schedule is missing, or notes already exist.
- `401` when the JWT is missing or invalid.
- `403` when the actor is not the assigned nurse.

## Business Rules

- Visit notes are encrypted at rest.
- Notes can only be created for `IN_PROGRESS` care requests.
- One active visit note record is allowed per care request.
- Creation emits an audit log.
- Patients and admins cannot create or modify visit notes.
