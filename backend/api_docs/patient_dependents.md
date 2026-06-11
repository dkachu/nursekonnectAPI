# Patient Dependents

## Purpose

Manage dependents who may receive care under a patient account.

## Endpoint URL

`/api/patient/dependents/`

`/api/patient/dependents/{id}/`

## HTTP Method

`GET`, `POST`, `PATCH`, `DELETE`

## Authentication

JWT access token required.

## Permissions

`IsPatientUser`

## Request Schema

```json
{
  "full_name": "Child Doe",
  "date_of_birth": "2018-01-01",
  "gender": "FEMALE",
  "relationship": "Child",
  "medical_notes": "Mild eczema"
}
```

## Response Schema

```json
{
  "id": 1,
  "full_name": "Child Doe",
  "date_of_birth": "2018-01-01",
  "gender": "FEMALE",
  "relationship": "Child",
  "medical_notes": "Mild eczema",
  "created_at": "2026-06-11T10:00:00Z",
  "updated_at": "2026-06-11T10:00:00Z"
}
```

List responses return an array of this object. Delete returns `204 No Content`.

## Error Responses

- `401 Unauthorized`: missing or invalid JWT.
- `403 Forbidden`: authenticated user is not a patient.
- `404 Not Found`: dependent does not belong to the patient.
- `400 Bad Request`: invalid input.

## Business Rules

- Patients may manage only their own dependents.
- Dependent medical notes are encrypted at rest.
