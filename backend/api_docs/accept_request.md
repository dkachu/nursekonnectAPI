# Accept Care Request

## Purpose

Atomically assigns a pending care request to an eligible nurse.

## Endpoint URL

`/api/requests/{id}/accept/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Authenticated nurse.

## Request Schema

No request body.

## Response Schema

Returns the care request with `status = ACCEPTED` and the assigned nurse fields.

## Error Responses

- `400`: request is no longer pending or nurse is not eligible.
- `401`: missing or invalid JWT token.
- `403`: authenticated user is not a nurse.
- `404`: request does not exist.

## Business Rules

- Uses `transaction.atomic()` and `select_for_update()` to prevent double assignment.
- Only one nurse may own a request.
- Nurse must be email verified, phone verified, NCK verified, online, and available.
- Acceptance writes an audit log.
