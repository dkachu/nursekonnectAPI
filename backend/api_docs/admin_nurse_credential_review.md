# Admin Nurse Credential Review

## Purpose
Allow authorized administrators to review uploaded nurse credentials.

## Endpoint URL
`/api/admin/nurses/{nurse_id}/credentials/{credential_id}/review/`

## HTTP Method
`PATCH`

## Authentication
JWT bearer token required.

## Permissions
`IsAuthorizedAdmin`

## Request Schema
```json
{
  "verification_status": "VERIFIED",
  "review_notes": "Valid document"
}
```

## Response Schema
Returns the reviewed credential with reviewer, review timestamp, status, and notes.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a staff administrator.
- `404` when the nurse or credential is not found.
- `400` when review status is unsupported.

## Business Rules
- Only staff users with `role=ADMIN` may review credentials.
- Review metadata is written by the service layer.
