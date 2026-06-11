# Mark Arrived

## Purpose

Transitions an en-route care request to `ARRIVED`.

## Endpoint URL

`/api/requests/{id}/arrived/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Assigned nurse only.

## Request Schema

No request body.

## Response Schema

Returns the care request with `status = ARRIVED`.

## Error Responses

- `400`: request is not `NURSE_EN_ROUTE`.
- `401`: missing or invalid JWT token.
- `403`: actor is not the assigned nurse.
- `404`: request does not exist.

## Business Rules

- Arrival distance validation will be enforced by the tracking phase.
- Writes an audit log.
