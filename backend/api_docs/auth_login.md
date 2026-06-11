# Auth Login

## Purpose

Authenticate a user with email and password and issue JWT credentials.

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
  "refresh": "jwt_refresh_token",
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

## Error Responses

- `401 Unauthorized`: invalid credentials or inactive account.

## Business Rules

- Authentication uses email only.
- Usernames are not supported.
- Inactive accounts cannot authenticate.
