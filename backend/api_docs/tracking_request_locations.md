# Tracking Request Locations

## Purpose
Return recent nurse GPS tracking points for a visible care request.

## Endpoint URL
`/api/tracking/requests/{request_id}/locations/`

## HTTP Method
`GET`

## Authentication
JWT access token required.

## Permissions
- Patient who owns the request.
- Assigned nurse for the request.
- Authorized administrator.

## Request Schema
No request body.

## Response Schema
Array of tracking location objects:

```json
[
  {
    "id": 1,
    "care_request_id": 10,
    "latitude": -1.286389,
    "longitude": 36.817223,
    "recorded_at": "2026-06-11T10:00:00Z",
    "accuracy_meters": 12,
    "location_stale": false,
    "created_at": "2026-06-11T10:00:00Z",
    "updated_at": "2026-06-11T10:00:00Z"
  }
]
```

## Error Responses
- `401 Unauthorized` when no valid token is supplied.
- `403 Forbidden` when the actor can see the request but is not allowed to track it.
- `404 Not Found` when the request is not visible to the actor.

## Business Rules
- Unassigned nurses must not read request tracking history.
- Patients can only read tracking history for their own requests.
- Locations are stored as PostGIS points and serialized as latitude/longitude for mobile clients.
- Location freshness is calculated using the configured 15-minute stale window.
