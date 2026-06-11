# OpenAPI Schema

## Purpose

Serve the OpenAPI 3 schema for NurseKonnect API clients and documentation tools.

## Endpoint URL

`/api/schema/`

## HTTP Method

`GET`

## Authentication

None.

## Permissions

Public read-only schema access.

## Request Schema

No request body.

## Response Schema

Returns `application/yaml` OpenAPI 3.0 content.

## Error Responses

- `500` if the `OPENAPI.yaml` artifact is missing from the deployment package.

## Business Rules

- The schema file is generated and versioned at repository root as `OPENAPI.yaml`.
