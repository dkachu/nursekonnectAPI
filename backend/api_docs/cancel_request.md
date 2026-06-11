# Cancel Care Request

## Purpose

Cancels a non-terminal care request.

## Endpoint URL

`/api/requests/{id}/cancel/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Patient owner, assigned nurse, or staff administrator.

## Request Schema

```json
{
  "reason": "Patient requested cancellation."
}
```

## Response Schema

Returns the care request with `status = CANCELLED`.

## Error Responses

- `400`: request is already terminal.
- `401`: missing or invalid JWT token.
- `403`: actor cannot cancel this request.
- `404`: request does not exist.

## Business Rules

- Cancellation writes an audit log.
- Assigned nurse status is returned to `ONLINE`.
- Medical data is never hard-deleted.
