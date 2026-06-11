# Nurse Status

## Purpose
Allow nurses to switch between online, busy, and offline states.

## Endpoint URL
`/api/nurse/status/`

## HTTP Method
`POST`

## Authentication
JWT bearer token required.

## Permissions
`IsNurseUser`

## Request Schema
```json
{
  "status": "ONLINE",
  "location_visible": true
}
```

## Response Schema
Returns the updated nurse profile.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a nurse.
- `400` when the nurse is not eligible to go online.

## Business Rules
- Nurses cannot go `ONLINE` unless platform availability is true.
- Platform availability requires verified email, verified phone, verified NCK status, and a non-expired license.
- `BUSY` and `OFFLINE` always hide nurse location visibility.
