# API Integration

`src/api/client.ts` and the domain API modules map backend endpoints to frontend services and hooks. The client provides:

- Base URL configuration.
- Authorization header attachment.
- Refresh token retry.
- Safe error message extraction.

TanStack Query manages server state. Sensitive medical data should use short cache lifetimes and remain available only to authorized routes and backend-permitted users.

OpenAPI-aligned DTOs live in `src/types/openapi.generated.ts`. Update this file from `../OPENAPI.yaml` before release when backend schemas change.
