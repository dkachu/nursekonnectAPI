# Nurse Specializations

## Purpose
List supported nurse specializations and allow nurses to set their own specialization list.

## Endpoint URL
`/api/nurse/specializations/`

`/api/nurse/profile/specializations/`

## HTTP Method
`GET`, `PUT`

## Authentication
JWT bearer token required.

## Permissions
`IsNurseUser`

## Request Schema
`PUT /api/nurse/profile/specializations/`

```json
{
  "specializations": ["GENERAL_NURSING", "WOUND_CARE"]
}
```

## Response Schema
Returns the specialization catalog for `GET` or the updated nurse profile for `PUT`.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a nurse.
- `400` when one or more specialization codes are unsupported.

## Business Rules
- Specializations are selected from the seeded catalog only.
- Updating specializations replaces the full current set.
