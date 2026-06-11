# Auth Verify OTP

## Purpose

Verify an authenticated user's email or phone OTP.

## Endpoint URL

`/api/auth/verify-otp/`

## HTTP Method

`POST`

## Authentication

JWT access token required.

## Permissions

`IsAuthenticated`

## Request Schema

```json
{
  "purpose": "EMAIL",
  "code": "123456"
}
```

## Response Schema

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "PATIENT",
    "email_verified": true,
    "phone_verified": false
  }
}
```

## Error Responses

- `401 Unauthorized`: missing or invalid access token.
- `400 Bad Request`: invalid purpose, invalid OTP, consumed OTP, or expired OTP.

## Business Rules

- Supported purposes are `EMAIL` and `PHONE`.
- OTPs are stored hashed.
- Successful verification consumes the OTP.
- Email verification sets `email_verified=true`.
- Phone verification sets `phone_verified=true`.
