# Patient Medical Information

## Purpose

Read protected medical information for an authorized actor.

## Endpoint URL

`/api/patients/{id}/medical-information/`

## HTTP Method

`GET`

## Authentication

JWT access token required.

## Permissions

`IsPatientMedicalActor`

## Request Schema

No request body.

## Response Schema

```json
{
  "id": 1,
  "allergies": "Penicillin",
  "chronic_conditions": "Asthma",
  "current_medications": "Salbutamol",
  "disabilities": "",
  "medical_notes": "Prefers morning visits",
  "blood_group": "O+"
}
```

## Error Responses

- `401 Unauthorized`: missing or invalid JWT.
- `403 Forbidden`: actor is not the patient, an assigned nurse, or an authorized admin.
- `404 Not Found`: patient profile does not exist.

## Business Rules

- Patient medical information is hidden by default.
- Access is allowed only to the patient, assigned nurse, or authorized admin.
- Assigned nurse access is denied until the request assignment domain is implemented.
- Authorized admin access requires `role=ADMIN` and staff status.
- Every successful read creates a medical access log.
- Protected medical fields are encrypted at rest.
