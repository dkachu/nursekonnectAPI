# Notifications Unread Count

## Purpose
Return the number of unread in-app notifications for the authenticated user.

## Endpoint URL
`/api/notifications/unread-count/`

## HTTP Method
`GET`

## Authentication
JWT bearer access token.

## Permissions
`IsAuthenticated`.

## Request Schema
No request body.

## Response Schema
```json
{
  "unread_count": 3
}
```

## Error Responses
- `401 Unauthorized` when the access token is missing or invalid.

## Business Rules
- Count only notifications owned by the authenticated user.
