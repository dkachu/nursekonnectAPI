# Location Update

## Purpose
Update the authenticated patient or nurse current location using browser/mobile GPS coordinates.

## Endpoint URL
`/api/location/update/`

## HTTP Method
`POST`

## Authentication
JWT bearer token required.

## Permissions
Authenticated patient or authenticated nurse.

## Request Schema
```json
{
  "latitude": -1.286389,
  "longitude": 36.817223,
  "source": "GPS",
  "accuracy_meters": 12
}
```

## Response Schema
```json
{
  "id": 1,
  "role": "PATIENT",
  "last_location_update": "2026-06-11T08:41:00Z",
  "location_stale": false
}
```

## Error Responses
- `401` when unauthenticated.
- `403` when the authenticated role cannot update location.
- `400` when coordinates are out of range or source is not `GPS`.
- `404` when the authenticated user has no matching profile.

## Business Rules
- Location input must come from browser/mobile GPS.
- Manual coordinate entry is rejected by requiring `source = "GPS"`.
- Coordinates are converted into `PointField(geography=True, srid=4326)`.
- Latitude and longitude are not stored separately for matching.
- `last_location_update` is updated atomically with `current_location`.
- Locations older than 15 minutes are stale.
