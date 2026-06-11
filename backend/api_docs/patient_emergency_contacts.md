# Patient Emergency Contacts

## Purpose

Manage emergency contacts for the authenticated patient.

## Endpoint URL

`/api/patient/emergency-contacts/`

`/api/patient/emergency-contacts/{id}/`

## HTTP Method

`GET`, `POST`, `PATCH`, `DELETE`

## Authentication

JWT access token required.

## Permissions

`IsPatientUser`

## Request Schema

```json
{
  "name": "Mary Doe",
  "phone_number": "+254700000001",
  "relationship": "Spouse"
}
```

## Response Schema

```json
{
  "id": 1,
  "name": "Mary Doe",
  "phone_number": "+254700000001",
  "relationship": "Spouse",
  "created_at": "2026-06-11T10:00:00Z",
  "updated_at": "2026-06-11T10:00:00Z"
}
```

List responses return an array of this object. Delete returns `204 No Content`.

## Error Responses

- `401 Unauthorized`: missing or invalid JWT.
- `403 Forbidden`: authenticated user is not a patient.
- `404 Not Found`: contact does not belong to the patient.
- `400 Bad Request`: invalid input.

## Business Rules

- Patients may manage only their own emergency contacts.
- Minimum emergency contact requirements are enforced when care-request eligibility is implemented.
