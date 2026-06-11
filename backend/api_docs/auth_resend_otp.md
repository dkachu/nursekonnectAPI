# Auth Resend OTP

## Purpose

Create a replacement OTP for the authenticated user's email or phone verification.

## Endpoint URL

`/api/auth/resend-otp/`

## HTTP Method

`POST`

## Authentication

JWT access token required.

## Permissions

`IsAuthenticated`

## Request Schema

```json
{
  "purpose": "PHONE"
}
```

## Response Schema

```json
{
  "expires_at": "2026-06-11T10:20:00Z"
}
```

## Error Responses

- `401 Unauthorized`: missing or invalid access token.
- `400 Bad Request`: invalid purpose.

## Business Rules

- Supported purposes are `EMAIL` and `PHONE`.
- Existing unconsumed OTPs for the same user and purpose are consumed before creating the replacement.
- OTP codes are not returned by the API response.
