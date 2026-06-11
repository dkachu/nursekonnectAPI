# Notifications List

## Purpose
List in-app workflow notifications for the authenticated user.

## Endpoint URL
`/api/notifications/`

## HTTP Method
`GET`

## Authentication
JWT bearer access token.

## Permissions
`IsAuthenticated`; users may only see their own notifications.

## Request Schema
No request body.

## Response Schema
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "notification_type": "JOB_ASSIGNED",
      "title": "New request nearby",
      "message": "A patient needs care nearby.",
      "is_read": false,
      "payload": {},
      "resource": "CareRequest",
      "resource_id": "10",
      "created_at": "2026-06-11T17:00:00Z",
      "updated_at": "2026-06-11T17:00:00Z"
    }
  ]
}
```

## Error Responses
- `401 Unauthorized` when the access token is missing or invalid.

## Business Rules
- Notifications are scoped to the authenticated recipient.
- Protected patient medical data must not be included in notification bodies or payloads.
