# Admin Nurse List

## Purpose
List nurse profiles for administrator verification and monitoring workflows.

## Endpoint URL
`/api/admin/nurses/`

## HTTP Method
`GET`

## Authentication
JWT access token required.

## Permissions
Authorized administrators only: `role=ADMIN` and `is_staff=True`.

## Request Schema
No request body.

## Response Schema
Array of nurse profile objects, including profile, verification, availability, specialization, and reputation fields.

## Error Responses
- `401 Unauthorized` when no valid token is supplied.
- `403 Forbidden` when the actor is not an authorized administrator.

## Business Rules
- Business authorization must use `user.role`, not `is_staff` alone.
- Results are optimized with related user and specialization data.
- Protected patient medical information is never returned.
