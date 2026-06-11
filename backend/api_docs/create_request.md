# Create Care Request

## Purpose

Creates a home-based care request for the authenticated patient using the patient's fresh GPS location.

## Endpoint URL

`/api/requests/`

## HTTP Method

`POST`

## Authentication

JWT bearer token required.

## Permissions

Authenticated patient account.

## Request Schema

```json
{
  "dependent_id": 4,
  "service_type": "WOUND_CARE",
  "priority": "URGENT",
  "description": "Dressing change needed.",
  "requested_time": "2026-06-11T14:00:00+03:00"
}
```

## Response Schema

Returns the care request with `status = PENDING`.

## Error Responses

- `400`: missing fresh patient GPS location, unverified patient account, invalid dependent, invalid service type, or invalid priority.
- `401`: missing or invalid JWT token.
- `403`: authenticated user is not the patient owner.

## Business Rules

- Patient email and phone must be verified.
- Location comes from the patient's stored browser/mobile GPS update.
- Manual request coordinates are not accepted.
- Request creation writes an audit log.
