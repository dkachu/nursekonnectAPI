# Admin Nurse Credential List

## Purpose
List uploaded credentials for a nurse selected by an administrator.

## Endpoint URL
`/api/admin/nurses/{nurse_id}/credentials/`

## HTTP Method
`GET`

## Authentication
JWT access token required.

## Permissions
Authorized administrators only: `role=ADMIN` and `is_staff=True`.

## Request Schema
No request body.

## Response Schema
Array of credential objects:

```json
[
  {
    "id": 1,
    "credential_type": "NCK_LICENSE",
    "image": "https://example.com/media/nurse_credentials/license.png",
    "verification_status": "PENDING",
    "reviewed_by": null,
    "reviewed_at": null,
    "review_notes": "",
    "created_at": "2026-06-11T10:00:00Z",
    "updated_at": "2026-06-11T10:00:00Z"
  }
]
```

## Error Responses
- `401 Unauthorized` when no valid token is supplied.
- `403 Forbidden` when the actor is not an authorized administrator.
- `404 Not Found` when the nurse does not exist.

## Business Rules
- Credentials are listed only for administrator review.
- Credential review decisions must be submitted to the credential review endpoint.
- Protected patient medical information is never returned.
