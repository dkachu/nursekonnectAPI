# Auth Refresh

## Purpose

Rotate a refresh token and issue a new access and refresh token pair.

## Endpoint URL

`/api/auth/refresh/`

## HTTP Method

`POST`

## Authentication

Not required.

## Permissions

`AllowAny`

## Request Schema

```json
{
  "refresh": "jwt_refresh_token"
}
```

## Response Schema

```json
{
  "access": "new_jwt_access_token",
  "refresh": "new_jwt_refresh_token"
}
```

## Error Responses

- `400 Bad Request`: missing, invalid, expired, or blacklisted refresh token.

## Business Rules

- Refresh tokens rotate.
- Old refresh tokens are blacklisted when rotation succeeds.
