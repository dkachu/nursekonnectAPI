# Error Monitoring

NurseKonnect uses `ErrorBoundary` to capture render-time failures and display a safe recovery screen without exposing healthcare data.

Runtime and API monitoring flows through `MonitoringService`.

Current behavior:

- Runtime errors are captured by `ErrorBoundary`.
- API errors are normalized through `getApiErrorMessage`.
- Sensitive payloads, JWTs, and healthcare records are not logged to the browser console.
- Vendor integration is intentionally deferred until a production monitoring provider is selected.

Production integration requirements:

- Configure a monitoring provider that supports data scrubbing.
- Disable collection of request bodies and authorization headers.
- Tag events by route and role only, not by patient clinical details.
- Route critical errors to operations alerting.
