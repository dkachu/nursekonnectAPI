# Auth Register

## Purpose

Create a patient or nurse account using email authentication and automatically create the matching profile.

## Endpoint URL

`/api/auth/register/`

## HTTP Method

`POST`

## Authentication

Not required.

## Permissions

`AllowAny`

## Request Schema

```json
{
  "email": "patient@example.com",
  "password": "StrongPassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+254712345678",
  "role": "PATIENT"
}
```

## Response Schema

```json
{
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "PATIENT",
    "email_verified": false,
    "phone_verified": false
  }
}
```

## Error Responses

- `400 Bad Request`: invalid email, weak password, invalid phone number, duplicate email, or unsupported role.

## Business Rules

- Only `PATIENT` and `NURSE` may self-register.
- Admin users are created administratively, not through public registration.
- Patient registration creates `PatientProfile`.
- Nurse registration creates `NurseProfile` with pending NCK verification and unavailable status.
- Email and phone verification OTP records are created.
