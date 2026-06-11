# Auth Login

## Purpose

Authenticate a user with email and password, return a short-lived access token, and set the refresh token in an HttpOnly cookie.

## Endpoint URL

`/api/auth/login/`

## HTTP Method

`POST`

## Authentication

Not required.

## Permissions

`AllowAny`

## Request Schema

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

## Response Schema

```json
{
  "access": "jwt_access_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "PATIENT",
    "email_verified": false,
    "phone_verified": false
  }
}
```

The response also sets:

```http
Set-Cookie: nursekonnect_refresh=<jwt_refresh_token>; HttpOnly; Secure; SameSite=Lax; Path=/api/auth/
```

## Error Responses

- `401 Unauthorized`: invalid credentials or inactive account.

## Business Rules

- Authentication uses email only.
- Usernames are not supported.
- Inactive accounts cannot authenticate.
- Refresh tokens are not returned in the response body for browser clients.
- Refresh tokens are stored in an HttpOnly cookie and rotated by `/api/auth/refresh/`.
