# Nurse Credentials

## Purpose
Allow nurses to upload credential images for compliance review.

## Endpoint URL
`/api/nurse/credentials/`

## HTTP Method
`GET`, `POST`

## Authentication
JWT bearer token required.

## Permissions
`IsNurseUser`

## Request Schema
Multipart form data:

```json
{
  "credential_type": "NCK_LICENSE",
  "image": "<image file>"
}
```

## Response Schema
Returns credential id, type, image URL/path, verification status, review metadata, and timestamps.

## Error Responses
- `401` when unauthenticated.
- `403` when the user is not a nurse.
- `400` when image or credential type is invalid.

## Business Rules
- Credential files use `ImageField`.
- Uploaded credentials start in `PENDING`.
- Nurses can only list and upload credentials for their own profile.
