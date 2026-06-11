# Care Request Detail

## Purpose

Returns one care request visible to the authenticated user.

## Endpoint URL

`/api/requests/{id}/`

## HTTP Method

`GET`

## Authentication

JWT bearer token required.

## Permissions

Authenticated patient owner, assigned nurse, nurse viewing pending unassigned request, or staff administrator.

## Request Schema

No request body.

## Response Schema

Returns the same care request shape as `GET /api/requests/`.

## Error Responses

- `401`: missing or invalid JWT token.
- `404`: request is not visible to the actor.

## Business Rules

- Pending request details are privacy-safe for nurses.
- No protected medical data, emergency contacts, exact GPS coordinates, or full address are returned.
