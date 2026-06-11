# Auth Logout

## Purpose

Logout a user by blacklisting the refresh token and clearing the refresh cookie.

## Endpoint URL

`/api/auth/logout/`

## HTTP Method

`POST`

## Authentication

JWT access token required.

## Permissions

`IsAuthenticated`

## Request Schema

No body is required for browser clients. The refresh token is read from the `nursekonnect_refresh` HttpOnly cookie.

Non-browser API clients may submit a fallback body:

```json
{
  "refresh": "jwt_refresh_token"
}
```

## Response Schema

`204 No Content`

## Error Responses

- `401 Unauthorized`: missing or invalid access token.
- `400 Bad Request`: missing, invalid, expired, or already blacklisted refresh token.

## Business Rules

- Logout does not delete the user.
- The refresh token is blacklisted when present.
- The refresh cookie is cleared.
