# Admin Nurse Verification

## Purpose
Allow authorized administrators to update NCK verification status.

## Endpoint URL
`/api/admin/nurses/{nurse_id}/verification/`

## HTTP Method
`PATCH`

## Authentication
JWT bearer token required.

## Permissions
`IsAuthorizedAdmin`

## Request Schema
```json
{
  "nck_license_number": "NCK-12345",
  "nck_license_expiry": "2030-01-01",
  "nck_verification_status": "VERIFIED"
}
```

## Response Schema
Returns the updated nurse profile and platform availability gate.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a staff administrator.
- `404` when nurse profile does not exist.
- `400` when verification rules fail.

## Business Rules
- Verification states are `PENDING`, `UNDER_REVIEW`, `VERIFIED`, `REJECTED`, and `EXPIRED`.
- `VERIFIED` requires an NCK license number and future expiry date.
- Expired or rejected nurses are unavailable for requests.
