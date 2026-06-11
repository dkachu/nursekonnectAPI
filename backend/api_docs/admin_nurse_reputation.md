# Admin Nurse Reputation Recalculation

## Purpose
Recalculate a nurse reputation score from stored rating and performance inputs.

## Endpoint URL
`/api/admin/nurses/{nurse_id}/reputation/recalculate/`

## HTTP Method
`POST`

## Authentication
JWT bearer token required.

## Permissions
`IsAuthorizedAdmin`

## Request Schema
No request body is required.

## Response Schema
Returns the nurse profile with updated `reputation_score`.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a staff administrator.
- `404` when nurse profile does not exist.

## Business Rules
- Reputation combines rating, completion rate, and response speed.
- Ratings and request-derived metrics are system-controlled fields.
