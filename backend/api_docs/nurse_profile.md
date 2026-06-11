# Nurse Profile

## Purpose
Allow an authenticated nurse to read and update their own profile.

## Endpoint URL
`/api/nurse/profile/`

## HTTP Method
`GET`, `PATCH`

## Authentication
JWT bearer token required.

## Permissions
`IsNurseUser`

## Request Schema
`PATCH` accepts partial profile fields such as:

```json
{
  "national_id": "12345678",
  "gender": "FEMALE",
  "date_of_birth": "1988-01-01",
  "years_of_experience": 8,
  "bio": "Home care nurse",
  "county": "Nairobi",
  "address": "Kilimani",
  "travel_radius_km": 50
}
```

## Response Schema
Returns nurse profile, verification state, specializations, availability gate, status, rating, and reputation score.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a nurse.
- `400` when submitted fields fail validation.

## Business Rules
- Nurses may only update their own profile.
- `nck_verification_status`, `is_available`, `rating`, and `reputation_score` are system-controlled.
- Platform availability is refreshed after profile updates.
