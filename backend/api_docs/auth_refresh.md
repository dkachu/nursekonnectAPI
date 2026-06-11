# Auth Refresh

## Purpose

Rotate a refresh token from the HttpOnly cookie and issue a new access token.

## Endpoint URL

`/api/auth/refresh/`

## HTTP Method

`POST`

## Authentication

Not required.

## Permissions

`AllowAny`

## Request Schema

No request body is required for browser clients. The refresh token is read from the `nursekonnect_refresh` HttpOnly cookie.

Non-browser API clients may submit a fallback body:

```json
{
  "refresh": "jwt_refresh_token"
}
```

## Response Schema

```json
{
  "access": "new_jwt_access_token"
}
```

The response also sets a rotated refresh cookie.

## Error Responses

- `400 Bad Request`: missing, invalid, expired, or blacklisted refresh token.

## Business Rules

- Refresh tokens rotate.
- Old refresh tokens are blacklisted when rotation succeeds.
- Refresh tokens are not returned in the response body.
