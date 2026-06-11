# Nearby Nurses

## Purpose

Returns verified, online, available, location-visible nurses near the authenticated patient using PostGIS candidate filtering and OSRM road-network distance/ETA.

## Endpoint URL

`/api/nurses/nearby/`

## HTTP Method

`GET`

## Authentication

JWT bearer token required.

## Permissions

`IsPatient`

Only authenticated patients may discover nearby nurses.

## Request Schema

Query parameters:

```json
{
  "specialization": "WOUND_CARE",
  "limit": 20
}
```

Fields:

- `specialization`: optional nurse specialization code. Supported values are the configured nurse specialization catalog.
- `limit`: optional integer from `1` to `50`. Defaults to `20`.

## Response Schema

```json
[
  {
    "id": 12,
    "first_name": "Jane",
    "last_name": "Wanjiku",
    "profile_photo": "",
    "years_of_experience": 5,
    "rating": "4.50",
    "reputation_score": "92.00",
    "average_response_seconds": 45,
    "specializations": [
      {
        "code": "WOUND_CARE",
        "name": "Wound care"
      }
    ],
    "specialization_match": true,
    "distance_km": 12.4,
    "estimated_travel_time": 18
  }
]
```

The response does not expose nurse GPS coordinates, phone numbers, email addresses, national IDs, license numbers, addresses, or credentials.

## Error Responses

`400 Bad Request`

```json
{
  "detail": "Fresh patient GPS location is required before discovering nurses."
}
```

Returned when the patient has not submitted a GPS location or the location is stale.

`400 Bad Request`

```json
{
  "specialization": ["\"INVALID\" is not a valid choice."]
}
```

Returned when an unsupported specialization code is requested.

`401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

`403 Forbidden`

```json
{
  "detail": "You do not have permission to perform this action."
}
```

Returned when the authenticated user is not a patient.

## Business Rules

- Eligible nurses must be `VERIFIED`.
- Eligible nurses must have `status = ONLINE`.
- Eligible nurses must have `is_available = true`.
- Eligible nurses must have `location_visible = true`.
- Eligible nurses must have a fresh location within the configured 15 minute stale window.
- PostGIS filters candidates inside the configured 100km search radius.
- OSRM provides the final road-network `distance_km` and `estimated_travel_time`.
- Straight-line PostGIS distance is never returned as the public distance.
- OSRM routes over 100km are excluded even if the PostGIS candidate prefilter matched.
- Results are ranked by:
  1. OSRM road distance
  2. Reputation score
  3. Average response speed
  4. Specialization match
- OSRM failures for individual candidates are skipped instead of falling back to straight-line estimates.
