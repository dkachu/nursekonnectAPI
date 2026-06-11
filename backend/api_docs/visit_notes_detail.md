# Visit Note Detail

## Purpose

Read or update one protected visit note.

## Endpoint URL

`/api/visit-notes/{id}/`

## HTTP Method

`GET`, `PATCH`

## Authentication

JWT bearer token required.

## Permissions

- `GET`: patient owner, assigned nurse, or authorized admin.
- `PATCH`: assigned nurse only.

## Request Schema

`GET` has no request body.

`PATCH` accepts any subset:

```json
{
  "vitals": "BP 118/76",
  "observations": "Improving",
  "medication_given": "None",
  "recommendations": "Continue wound care",
  "follow_up_required": true,
  "follow_up_schedule": "1_WEEK"
}
```

## Response Schema

```json
{
  "id": 10,
  "care_request_id": 42,
  "patient_id": 7,
  "nurse_id": 3,
  "nurse_name": "Jane Wanjiku",
  "vitals": "BP 118/76",
  "observations": "Improving",
  "medication_given": "None",
  "recommendations": "Continue wound care",
  "follow_up_required": true,
  "follow_up_schedule": "1_WEEK",
  "follow_up_due_at": "2026-06-18T10:00:00Z",
  "created_at": "2026-06-11T10:00:00Z",
  "updated_at": "2026-06-11T10:05:00Z"
}
```

## Error Responses

- `400` when follow-up validation fails or the visit state is invalid.
- `401` when the JWT is missing or invalid.
- `403` when the actor is not allowed to update the note.
- `404` when the note is not visible to the actor.

## Business Rules

- Reads create medical access logs.
- Updates emit audit logs.
- Follow-up due dates are calculated from the selected supported schedule.
- Visit note data is protected medical information and is hidden by default.
