# Patient Profile

## Purpose

Read or update the authenticated patient's profile, including protected medical fields for the owner.

## Endpoint URL

`/api/patient/profile/`

## HTTP Method

`GET`, `PATCH`

## Authentication

JWT access token required.

## Permissions

`IsPatientUser`

## Request Schema

`GET` has no body.

`PATCH` accepts any editable subset:

```json
{
  "national_id": "12345678",
  "gender": "FEMALE",
  "date_of_birth": "1990-01-01",
  "blood_group": "O+",
  "allergies": "Penicillin",
  "chronic_conditions": "Asthma",
  "current_medications": "Salbutamol",
  "disabilities": "",
  "medical_notes": "Prefers morning visits",
  "county": "Nairobi",
  "address": "Westlands"
}
```

## Response Schema

```json
{
  "id": 1,
  "email": "patient@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+254712345678",
  "phone_verified": false,
  "email_verified": false,
  "national_id": "12345678",
  "gender": "FEMALE",
  "date_of_birth": "1990-01-01",
  "blood_group": "O+",
  "allergies": "Penicillin",
  "chronic_conditions": "Asthma",
  "current_medications": "Salbutamol",
  "disabilities": "",
  "medical_notes": "Prefers morning visits",
  "county": "Nairobi",
  "address": "Westlands"
}
```

## Error Responses

- `401 Unauthorized`: missing or invalid JWT.
- `403 Forbidden`: authenticated user is not a patient.
- `400 Bad Request`: invalid field value.

## Business Rules

- Patients may read and update only their own profile.
- Protected medical fields are encrypted at rest.
- Reading protected medical fields creates a medical access log.
