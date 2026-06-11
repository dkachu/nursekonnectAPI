# Swagger UI

## Purpose

Render interactive Swagger documentation for the NurseKonnect API.

## Endpoint URL

`/api/docs/swagger/`

## HTTP Method

`GET`

## Authentication

None.

## Permissions

Public read-only documentation access.

## Request Schema

No request body.

## Response Schema

Returns HTML that loads Swagger UI against `/api/schema/`.

## Error Responses

- `500` if static documentation assets cannot load in the client environment.

## Business Rules

- This endpoint must not expose secrets or protected patient data.
