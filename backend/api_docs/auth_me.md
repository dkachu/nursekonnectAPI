# Auth Current User

## Purpose

Return the authenticated user's identity and non-medical profile metadata for secure frontend session restoration.

## Endpoint URL

`/api/auth/me/`

## HTTP Method

`GET`

## Authentication

JWT access token required.

## Permissions

`IsAuthenticated`

## Request Schema

No request body.

## Response Schema

```json
{
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "PATIENT",
    "email_verified": true,
    "phone_verified": true,
    "profile": {
      "id": 10,
      "phone_number": "+254712345678",
      "county": "Nairobi",
      "address": "Westlands"
    }
  }
}
```

## Error Responses

- `401 Unauthorized`: missing, expired, or invalid access token.

## Business Rules

- Used after `/api/auth/refresh/` during frontend bootstrap.
- Profile metadata must not include protected medical fields.
- The endpoint must not return refresh tokens.
