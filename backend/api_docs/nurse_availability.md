# Nurse Availability

## Purpose
Allow nurses to manage recurring weekly availability slots.

## Endpoint URL
`/api/nurse/availability/`

`/api/nurse/availability/{slot_id}/`

## HTTP Method
`GET`, `POST`, `PATCH`, `DELETE`

## Authentication
JWT bearer token required.

## Permissions
`IsNurseUser`

## Request Schema
```json
{
  "day_of_week": 1,
  "start_time": "08:00",
  "end_time": "17:00"
}
```

## Response Schema
Returns availability slot id, day, start time, end time, and timestamps.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a nurse.
- `404` when the slot does not belong to the nurse.
- `400` when `start_time` is not before `end_time`.

## Business Rules
- Nurses can only manage their own availability slots.
- Duplicate slots for the same nurse/day/time window are rejected by the database constraint.
