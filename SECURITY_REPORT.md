# NurseKonnect Security Audit Report

## Scope

This audit reviewed the current backend implementation against `AGENTS.md`, `PLANS.md`, and the requested controls:

- JWT security
- Object-level permissions
- Rate limiting
- Audit logs
- Medical access logs
- Encryption
- Soft deletes
- Secure headers
- OWASP API Security risks

## Executive Summary

Security posture improved during this audit. The main vulnerabilities found were:

- Auth endpoints used only generic throttling instead of scoped abuse controls.
- Authentication events were not consistently audited.
- `IsAdmin` trusted `role=ADMIN` without also requiring staff authorization.
- Nurses could enumerate broad pending care requests instead of only assigned/offered requests.
- Pre-acceptance care request payloads exposed patient narrative/dependent details to nurses.
- Patient dependents and emergency contacts were hard-deleted instead of retained.
- Production startup did not require an explicit medical encryption key.

All items above were remediated and covered by regression tests.

## Fixes Applied

### JWT Security

- Confirmed Simple JWT access/refresh split.
- Confirmed access token lifetime is 15 minutes by default.
- Confirmed refresh rotation and blacklist-after-rotation are enabled.
- Confirmed logout blacklists submitted refresh tokens.
- Added authentication audit events for registration, login success, login failure, logout, OTP verify, and OTP resend.

### Object-Level Permissions

- Hardened `IsAdmin` so admin access now requires both:
  - `user.role == ADMIN`
  - `user.is_staff is True`
- Restricted nurse request visibility to:
  - assigned requests
  - requests with an active offer for that nurse
- Updated care request serialization so pre-acceptance nurse views hide:
  - patient last name
  - dependent ID/name
  - request description
  - requested time
  - lifecycle timestamps
  - cancellation reason

### Rate Limiting

- Added `ScopedRateThrottle`.
- Added scoped throttle buckets:
  - `auth_register`
  - `auth_login`
  - `auth_refresh`
  - `auth_logout`
  - `otp_verify`
  - `otp_resend`
- Test environment rates are raised to avoid false failures from shared test IPs.

### Audit Logs

- Added audit records for:
  - `AUTH_REGISTERED`
  - `AUTH_LOGIN_SUCCEEDED`
  - `AUTH_LOGIN_FAILED`
  - `AUTH_LOGGED_OUT`
  - `AUTH_OTP_VERIFIED`
  - `AUTH_OTP_RESENT`
- Existing request, visit, and sensitive workflow audit logging remains in place.

### Medical Access Logs

- Confirmed protected patient medical reads create `MedicalAccessLog` records.
- Confirmed visit note reads create `MedicalAccessLog` records.
- Existing tests verify unauthorized users do not create access logs for denied reads.

### Encryption

- Confirmed encrypted fields are stored with `EncryptedTextField`.
- Confirmed patient medical fields and dependent medical notes are encrypted at rest.
- Confirmed visit note clinical fields are encrypted at rest.
- Production now fails closed if `MEDICAL_DATA_FERNET_KEY` is not configured.

### Soft Deletes

- Added soft-delete fields to:
  - `EmergencyContact`
  - `PatientDependent`
- Updated delete services to call `mark_deleted()` instead of hard delete.
- Updated selectors to hide soft-deleted records from normal API responses.

### Secure Headers

- Confirmed:
  - `SECURE_CONTENT_TYPE_NOSNIFF = True`
  - `X_FRAME_OPTIONS = "DENY"`
  - secure production cookies
  - production HSTS
  - production HTTPS redirect
- Added:
  - `SECURE_REFERRER_POLICY = "same-origin"`
  - `CROSS_ORIGIN_OPENER_POLICY = "same-origin"`
- Production deploy check passes when valid production secrets are supplied.

## OWASP API Security Review

| OWASP Risk | Result |
|---|---|
| Broken Object Property Level Authorization | Improved: care request pre-acceptance serializer now hides sensitive fields. |
| Broken Authentication | Improved: scoped throttles and auth audit events added. JWT rotation/blacklist verified. |
| Broken Object Level Authorization | Improved: nurses can only see assigned/offered requests; admin permission requires staff. |
| Unrestricted Resource Consumption | Improved: auth and OTP endpoints now have scoped rate limits. |
| Broken Function Level Authorization | Verified: role permissions and service checks protect patient, nurse, admin, request, tracking, and visit workflows. |
| Unrestricted Access to Sensitive Business Flows | Improved: request enumeration by nurses is restricted to offers/assignments. |
| Server Side Request Forgery | No new SSRF surface found; OSRM URL remains configuration-controlled and should be private in production. |
| Security Misconfiguration | Improved: production now requires explicit secrets and secure headers are stronger. |
| Improper Inventory Management | Endpoint docs exist for implemented endpoints reviewed in scope. |
| Unsafe Consumption of APIs | OSRM failures are handled by matching/discovery services; production should use a controlled OSRM endpoint. |

## Verification

Commands run successfully:

```text
ruff check backend
black --check backend
docker compose exec -T -e DJANGO_ENV=test -e POSTGRES_TEST_HOST=postgres -e POSTGRES_TEST_PORT=5432 backend python manage.py makemigrations --check --dry-run
docker compose exec -T -e DJANGO_ENV=production ... backend python manage.py check --deploy
docker compose exec -T -e DJANGO_ENV=test ... backend python -m pytest
```

Results:

- Targeted security regression tests: 50 passed.
- Full backend test suite: 109 passed.
- Production deploy check: no issues when valid production secrets are supplied.
- Migration check: no changes detected.

## Residual Operational Requirements

- Set a real `DJANGO_SECRET_KEY` in production.
- Set a real `MEDICAL_DATA_FERNET_KEY` in production.
- Do not reuse example secrets.
- Keep PostgreSQL and Redis private to the application network.
- Terminate TLS at Nginx/load balancer and keep `DJANGO_SECURE_SSL_REDIRECT=true` in production.
- Replace public OSRM with a controlled OSRM service before production launch.
- Add provider-level SMS/email/push abuse controls when real notification providers are integrated.
- Add centralized log retention and alerting for failed login spikes, OTP abuse, and denied medical access attempts.
