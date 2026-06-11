# Tracking Location

## Purpose
Record a nurse GPS tracking point during journey tracking and refresh the nurse current location.

## Endpoint URL
`/api/tracking/location/`

## HTTP Method
`POST`

## Authentication
JWT bearer token required.

## Permissions
Authenticated nurse only.

## Request Schema
```json
{
  "latitude": -1.292066,
  "longitude": 36.821946,
  "source": "GPS",
  "accuracy_meters": 9
}
```

## Response Schema
```json
{
  "id": 1,
  "care_request_id": 10,
  "latitude": -1.292066,
  "longitude": 36.821946,
  "recorded_at": "2026-06-11T08:42:00Z",
  "accuracy_meters": 9,
  "location_stale": false,
  "created_at": "2026-06-11T08:42:00Z",
  "updated_at": "2026-06-11T08:42:00Z"
}
```

## Error Responses
- `401` when unauthenticated.
- `403` when the authenticated user is not a nurse.
- `400` when coordinates are out of range or source is not `GPS`.
- `400` when tracking updates are sent less than 30 seconds apart.
- `404` when the authenticated nurse has no active `NURSE_EN_ROUTE` request.

## Business Rules
- Nurse tracking points are stored as PostGIS geography points.
- Tracking is accepted only for the assigned nurse of an active en-route request.
- Tracking points are linked to the active care request.
- Tracking writes also refresh the nurse profile `current_location`.
- Tracking history is append-only for movement reconstruction.
- Frontends should send tracking updates every 30-60 seconds.
- Locations older than 15 minutes are stale and excluded from matching selectors.
