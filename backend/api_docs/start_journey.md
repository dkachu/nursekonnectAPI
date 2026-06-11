# Start Journey

## Purpose

Transitions an accepted care request to `NURSE_EN_ROUTE`.

## Endpoint URL

`/api/requests/{id}/start-journey/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Assigned nurse only.

## Request Schema

No request body.

## Response Schema

Returns the care request with `status = NURSE_EN_ROUTE`.

## Error Responses

- `400`: invalid status transition.
- `401`: missing or invalid JWT token.
- `403`: actor is not the assigned nurse.
- `404`: request does not exist.

## Business Rules

- Valid from `ACCEPTED` or `PREPARING`.
- Writes an audit log.
