# NCK License Status Redirect

## Purpose
Redirect users to the official Nursing Council of Kenya license status portal so they can independently verify a nurse.

## Endpoint URL
`/api/nurses/nck-license-status/`

## HTTP Method
`GET`

## Authentication
Not required.

## Permissions
Public.

## Request Schema
No request body is required.

## Response Schema
HTTP `302` redirect to:

```text
https://osp.nckenya.com/LicenseStatus
```

## Error Responses
No domain-specific error responses.

## Business Rules
- The backend redirects to the configured `NCK_LICENSE_STATUS_URL`.
- The default URL is the official NCK license status page.
- NurseKonnect still stores its own NCK verification state after administrator review.
- External user verification does not mutate nurse verification status inside NurseKonnect.
