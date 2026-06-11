# Complete Care Request

## Purpose

Transitions an in-progress care request to `COMPLETED`.

## Endpoint URL

`/api/requests/{id}/complete/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Assigned nurse only.

## Request Schema

No request body.

## Response Schema

Returns the care request with `status = COMPLETED`.

## Error Responses

- `400`: request is not `IN_PROGRESS`.
- `401`: missing or invalid JWT token.
- `403`: actor is not the assigned nurse.
- `404`: request does not exist.

## Business Rules

- Completion writes an audit log.
- Assigned nurse status is returned to `ONLINE`.
