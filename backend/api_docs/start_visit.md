# Start Visit

## Purpose

Transitions an arrived care request to `IN_PROGRESS`.

## Endpoint URL

`/api/requests/{id}/start-visit/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Assigned nurse only.

## Request Schema

No request body.

## Response Schema

Returns the care request with `status = IN_PROGRESS`.

## Error Responses

- `400`: request is not `ARRIVED`.
- `401`: missing or invalid JWT token.
- `403`: actor is not the assigned nurse.
- `404`: request does not exist.

## Business Rules

- Visit distance validation will be enforced by the tracking/visit phase.
- Writes an audit log.
