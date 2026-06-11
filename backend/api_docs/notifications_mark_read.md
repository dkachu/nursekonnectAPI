# Notifications Mark Read

## Purpose
Mark one authenticated-user notification as read.

## Endpoint URL
`/api/notifications/{notification_id}/mark-read/`

## HTTP Method
`POST`

## Authentication
JWT bearer access token.

## Permissions
`IsAuthenticated`; object ownership is enforced.

## Request Schema
No request body.

## Response Schema
Returns the updated notification.

## Error Responses
- `401 Unauthorized` when the access token is missing or invalid.
- `404 Not Found` when the notification does not exist or belongs to another user.

## Business Rules
- Users cannot mark another user's notification as read.
- The operation is idempotent for already-read notifications.
