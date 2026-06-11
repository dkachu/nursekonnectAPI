# Auth Logout

## Purpose

Logout a user by blacklisting a refresh token.

## Endpoint URL

`/api/auth/logout/`

## HTTP Method

`POST`

## Authentication

JWT access token required.

## Permissions

`IsAuthenticated`

## Request Schema

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
- The submitted refresh token is blacklisted.
