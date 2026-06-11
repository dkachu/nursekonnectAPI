# List Care Requests

## Purpose

Lists care requests visible to the authenticated user.

## Endpoint URL

`/api/requests/`

## HTTP Method

`GET`

## Authentication

JWT bearer token required.

## Permissions

Authenticated users.

## Request Schema

No request body.

## Response Schema

```json
[
  {
    "id": 10,
    "patient_first_name": "John",
    "patient_last_name": "Doe",
    "service_type": "GENERAL_NURSING",
    "priority": "NORMAL",
    "status": "PENDING",
    "assigned_nurse_id": null,
    "assigned_nurse_name": ""
  }
]
```

## Error Responses

- `401`: missing or invalid JWT token.

## Business Rules

- Patients see only their own requests.
- Nurses see unassigned pending requests and requests assigned to them.
- Staff administrators see all requests.
- Protected medical information is never included.
