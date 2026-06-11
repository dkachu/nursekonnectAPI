# Notifications Mark All Read

## Purpose
Mark all unread notifications for the authenticated user as read.

## Endpoint URL
`/api/notifications/mark-all-read/`

## HTTP Method
`POST`

## Authentication
JWT bearer access token.

## Permissions
`IsAuthenticated`.

## Request Schema
No request body.

## Response Schema
```json
{
  "updated_count": 3
}
```

## Error Responses
- `401 Unauthorized` when the access token is missing or invalid.

## Business Rules
- Only the authenticated user's unread notifications are updated.
