# List Visit Notes

## Purpose

List protected visit notes visible to the authenticated healthcare actor.

## Endpoint URL

`/api/visit-notes/`

## HTTP Method

`GET`

## Authentication

JWT bearer token required.

## Permissions

- Patient: own visit notes only.
- Nurse: notes for visits assigned to that nurse only.
- Authorized admin: all notes.

## Request Schema

No request body.

## Response Schema

```json
[
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
]
```

## Error Responses

- `401` when the JWT is missing or invalid.
- `403` when the authenticated user does not have a supported healthcare role.

## Business Rules

- Every returned note creates a medical access log.
- Querysets use `select_related()` for care request, patient, and nurse relationships.
- Unauthorized users receive no unrelated patient visit information.
