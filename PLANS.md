# NurseKonnect Implementation Plan

## 1. Source Of Truth

This plan is derived from `AGENTS.md` and treats it as the governing specification for NurseKonnect. The platform is a secure, API-first Django REST Framework backend for home-based care in Kenya, connecting patients with verified nurses while protecting medical information by default.

The golden rule for every phase is:

```text
Patient medical information is hidden by default.

Only the patient, the assigned nurse, and authorized administrators may access protected healthcare information.
```

No implementation phase may weaken this rule.

## 2. Architecture Decisions

### Core Stack

- Runtime: Python 3.12+
- Framework: Django 5+
- API: Django REST Framework
- Authentication: Email-based custom user model with JWT via Simple JWT
- Database: PostgreSQL with PostGIS
- Geospatial storage: `PointField(geography=True, srid=4326)`
- Background processing: Celery
- Broker/cache: Redis
- Deployment: Docker, Docker Compose, Gunicorn, Nginx
- Routing ETA: OSRM road-network calculations

### Project Layout

```text
nursekonnect/
|-- backend/
|   |-- api_docs/
|   |-- apps/
|   |   |-- accounts/
|   |   |-- patients/
|   |   |-- nurses/
|   |   |-- requests/
|   |   |-- tracking/
|   |   |-- visits/
|   |   |-- ratings/
|   |   |-- notifications/
|   |   `-- audit_logs/
|   |-- core/
|   |   |-- settings/
|   |   |   |-- base.py
|   |   |   |-- local.py
|   |   |   |-- test.py
|   |   |   `-- production.py
|   |   |-- celery.py
|   |   |-- urls.py
|   |   |-- asgi.py
|   |   `-- wsgi.py
|   |-- docker/
|   |-- Dockerfile
|   |-- manage.py
|   |-- requirements/
|   `-- README.md
|-- frontend/
|   |-- public/
|   |-- src/
|   |-- Dockerfile
|   |-- package.json
|   `-- README.md
|-- docker/
|   |-- nginx/
|   |-- osrm/
|   `-- compose/
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

### Architectural Style

- Thin API views and viewsets.
- Serializers validate transport-layer input and output.
- Service layer owns business rules and transactions.
- Selectors/query services own optimized reads.
- Permissions own role and object-level access.
- Celery tasks own asynchronous workflows.
- Audit logging is centralized and mandatory for sensitive actions.
- API documentation is endpoint-specific and stored under `backend/api_docs/`.

## 3. Django App Boundaries

### `accounts`

Owns identity and authentication.

Responsibilities:

- Custom email-only `User`
- Roles: `PATIENT`, `NURSE`, `ADMIN`
- JWT login, refresh, logout/blacklist
- Registration orchestration
- Email verification
- Phone OTP verification
- Authentication rate limiting hooks
- Auth-related audit events

Does not own:

- Patient medical profile data
- Nurse credential details beyond user identity

### `patients`

Owns patient domain data.

Responsibilities:

- `PatientProfile`
- `PatientDependent`
- `EmergencyContact`
- Patient favorites
- Patient nurse blocks
- Protected medical fields
- Patient profile permissions
- Medical access logging triggers

Sensitive fields:

- `allergies`
- `chronic_conditions`
- `current_medications`
- `medical_notes`

### `nurses`

Owns nurse domain data.

Responsibilities:

- `NurseProfile`
- NCK verification status
- Credentials
- Specializations
- Availability schedule
- Maximum travel radius
- Nurse online/busy/offline state
- Nurse location visibility
- License expiry monitoring metadata

### `requests`

Owns care request lifecycle.

Responsibilities:

- `CareRequest`
- Request offers to eligible nurses
- Request status transitions
- Atomic accept flow
- Cancellation flow
- Reassignment triggers
- Privacy-safe request serialization before acceptance

### `tracking`

Owns GPS tracking records and journey telemetry.

Responsibilities:

- Location update ingestion
- En-route nurse tracking history
- Current nurse location freshness
- Arrival distance validation support
- Patient tracking read model

### `visits`

Owns visit execution records.

Responsibilities:

- Visit start validation
- Visit completion
- Visit notes
- Follow-up schedule metadata
- Medical access logging for notes

### `ratings`

Owns rating and reputation inputs.

Responsibilities:

- Patient-to-nurse ratings
- Rating validation
- Rating visibility rules
- Reputation recalculation trigger

### `notifications`

Owns notification records and delivery orchestration.

Responsibilities:

- Notification event persistence
- Push/email/SMS delivery adapter interfaces
- Delivery status tracking
- Celery delivery tasks

### `audit_logs`

Owns immutable security and privacy logs.

Responsibilities:

- General audit logs
- Medical access logs
- Authentication event logs
- Sensitive action event logs
- Admin review queries

## 4. Model Relationship Plan

### Identity And Profiles

- `User` has one `PatientProfile` when `role=PATIENT`.
- `User` has one `NurseProfile` when `role=NURSE`.
- Admin users use `User.role=ADMIN`; they do not require patient or nurse profiles.

### Patient Domain

- `PatientProfile` belongs to `User`.
- `PatientDependent` belongs to `PatientProfile`.
- `EmergencyContact` belongs to `PatientProfile`.
- `PatientFavoriteNurse` links `PatientProfile` to `NurseProfile`.
- `PatientBlockedNurse` links `PatientProfile` to `NurseProfile`.

### Nurse Domain

- `NurseProfile` belongs to `User`.
- `NurseCredential` belongs to `NurseProfile`.
- `NurseSpecialization` is many-to-many with `NurseProfile`.
- `NurseAvailabilitySlot` belongs to `NurseProfile`.

### Requests And Visits

- `CareRequest` belongs to `PatientProfile`.
- `CareRequest` optionally belongs to `PatientDependent`.
- `CareRequest` optionally belongs to assigned `NurseProfile`.
- `RequestOffer` links `CareRequest` to candidate `NurseProfile`.
- `TrackingLocation` belongs to `NurseProfile` and optionally to `CareRequest`.
- `VisitNote` belongs to `CareRequest`, `PatientProfile`, and assigned `NurseProfile`.
- `Rating` belongs to `PatientProfile`, `NurseProfile`, and completed `CareRequest`.

### Logs And Notifications

- `Notification` belongs to recipient `User` and optionally references a domain resource.
- `AuditLog` belongs to actor `User` when authenticated.
- `MedicalAccessLog` belongs to actor `User`, patient `PatientProfile`, and referenced resource.

## 5. ERD Description

```text
User
  1--0..1 PatientProfile
  1--0..1 NurseProfile
  1--many AuditLog
  1--many Notification

PatientProfile
  1--many PatientDependent
  1--many EmergencyContact
  1--many CareRequest
  many--many NurseProfile through PatientFavoriteNurse
  many--many NurseProfile through PatientBlockedNurse
  1--many MedicalAccessLog
  1--many Rating

NurseProfile
  1--many NurseCredential
  many--many NurseSpecialization
  1--many NurseAvailabilitySlot
  1--many RequestOffer
  1--many TrackingLocation
  1--many VisitNote
  1--many Rating

CareRequest
  many--1 PatientProfile
  many--0..1 PatientDependent
  many--0..1 NurseProfile as assigned_nurse
  1--many RequestOffer
  1--many TrackingLocation
  1--0..1 VisitNote
  1--0..1 Rating

RequestOffer
  many--1 CareRequest
  many--1 NurseProfile

VisitNote
  many--1 CareRequest
  many--1 PatientProfile
  many--1 NurseProfile

Rating
  many--1 PatientProfile
  many--1 NurseProfile
  many--1 CareRequest

AuditLog
  many--0..1 User

MedicalAccessLog
  many--1 User
  many--1 PatientProfile
```

## 6. Authentication Architecture

### User Model

The custom user model must be email-only and based on:

```text
AbstractBaseUser
PermissionsMixin
```

Required fields:

- `id`
- `email`, unique and indexed
- `first_name`
- `last_name`
- `role`
- `is_active`
- `is_staff`
- `is_superuser`
- `email_verified`
- `phone_verified`
- `created_at`
- `updated_at`

Rules:

- `USERNAME_FIELD = "email"`
- `REQUIRED_FIELDS = []`
- No username field.
- Email is normalized before persistence.
- Business role checks use `user.role`, never `is_staff`.

### Registration

Patient registration creates:

- `User(role=PATIENT)`
- `PatientProfile`

Nurse registration creates:

- `User(role=NURSE)`
- `NurseProfile`

Nurses remain unavailable until:

- Email verified
- Phone verified
- NCK status is `VERIFIED`

### JWT

JWT uses Simple JWT:

- Short-lived access token
- Rotating refresh token
- Refresh blacklist after rotation
- Logout blacklists refresh token
- Failed login attempts are rate-limited and audited

### Verification

Email verification:

- Verification link and/or OTP
- Required before protected patient/nurse actions

Phone verification:

- SMS OTP
- E.164 Kenyan format support
- Required before care requests or nurse availability

## 7. Geospatial Architecture

### Storage

Use PostGIS geography points:

```text
PointField(geography=True, srid=4326)
```

Models requiring geography:

- `PatientProfile.current_location`
- `NurseProfile.current_location`
- `CareRequest.location`
- `TrackingLocation.location`

Rules:

- Do not store latitude and longitude separately for matching.
- API accepts latitude/longitude payloads from browser/mobile GPS only.
- Service layer converts payloads into PostGIS points.
- Spatial indexes are required on all active matching location fields.

### Freshness

`MAX_LOCATION_AGE = 15 minutes`

Nurse locations older than this are stale and excluded from matching.

### Distance And ETA

PostGIS is used for spatial filtering and indexing.

OSRM is used for road-network distance and ETA:

- Never present straight-line distance as final matching distance.
- Nearby query may use PostGIS as a candidate prefilter.
- Final response distance and ETA must come from OSRM.

Response shape:

```json
{
  "distance_km": 12.4,
  "estimated_travel_time": 18
}
```

## 8. Nurse Matching Architecture

### Eligibility Filter

A nurse is eligible only when all are true:

- `status = ONLINE`
- `is_available = True`
- `location_visible = True`
- `nck_verification_status = VERIFIED`
- location is fresh
- nurse is currently on shift
- patient has not blocked nurse
- request is inside nurse travel radius
- distance is within platform cap of 100km

### Ranking

Rank eligible nurses by:

1. Availability
2. OSRM road distance and ETA
3. Specialization match
4. Reputation score
5. Response speed

### Distribution

- Notify nearest 5 eligible nurses.
- Do not broadcast to all nurses.
- Each offer expires after 2 minutes.
- If no nurse accepts, expand radius gradually.
- Preserve privacy before acceptance.

### Acceptance Race Control

Acceptance must run inside `transaction.atomic()`.

Lock the care request row using row-level locking before assignment.

Only one nurse can transition the request from `PENDING` or offered state into accepted assignment.

## 9. Service Layer Design

### Service Modules

```text
apps/accounts/services/
  registration.py
  verification.py
  tokens.py

apps/patients/services/
  profiles.py
  medical_access.py
  emergency_contacts.py
  blocking.py
  favorites.py

apps/nurses/services/
  profiles.py
  credentials.py
  availability.py
  license_monitoring.py
  location_visibility.py

apps/requests/services/
  creation.py
  matching.py
  offers.py
  acceptance.py
  transitions.py
  cancellation.py

apps/tracking/services/
  location_updates.py
  arrival_validation.py
  journey_tracking.py

apps/visits/services/
  visit_start.py
  completion.py
  notes.py

apps/ratings/services/
  ratings.py
  reputation.py

apps/notifications/services/
  dispatch.py
  channels.py

apps/audit_logs/services/
  audit.py
  medical_access.py
```

### Design Rules

- Views call services.
- Services enforce business rules.
- Selectors encapsulate optimized reads.
- Serializers do not decide authorization.
- All sensitive service methods accept actor/user context.
- All medical-data reads call medical access logging.
- State transitions are explicit and validated.

## 10. API Dependency Map

### Authentication

- `POST /api/auth/register/`
  - Depends on `accounts.registration`
  - Creates profile in `patients` or `nurses`
  - Emits audit log

- `POST /api/auth/login/`
  - Depends on Simple JWT and account checks
  - Emits login audit log

- `POST /api/auth/logout/`
  - Depends on JWT blacklist
  - Emits logout audit log

- `POST /api/auth/refresh/`
  - Depends on Simple JWT refresh flow

- `POST /api/auth/verify-otp/`
  - Depends on verification service

- `POST /api/auth/resend-otp/`
  - Depends on notifications service

### Profiles

- `GET/PATCH /api/patient/profile/`
  - Depends on `patients.profiles`
  - Requires patient role
  - Logs protected medical access for sensitive reads

- `GET/PATCH /api/nurse/profile/`
  - Depends on `nurses.profiles`
  - Requires nurse role

### Location And Discovery

- `POST /api/location/update/`
  - Depends on `tracking.location_updates`
  - Updates patient or nurse current point

- `GET /api/nurses/nearby/`
  - Depends on PostGIS candidate filter
  - Depends on OSRM route calculations
  - Requires patient role

### Care Requests

- `POST /api/requests/`
  - Depends on patient profile, location, matching, notifications

- `GET /api/requests/`
  - Uses role-based selectors

- `GET /api/requests/{id}/`
  - Uses object-level permissions and privacy serializer

- `POST /api/requests/{id}/accept/`
  - Depends on request offer, atomic locking, notification

- `POST /api/requests/{id}/start-journey/`
  - Depends on assigned nurse permission

- `POST /api/requests/{id}/arrived/`
  - Depends on tracking and 100m validation

- `POST /api/requests/{id}/start-visit/`
  - Depends on assigned nurse permission and 100m validation

- `POST /api/requests/{id}/complete/`
  - Depends on visit completion and notification

- `POST /api/requests/{id}/cancel/`
  - Depends on cancellation rules and reassignment workflow

### Tracking, Visits, Ratings

- `POST /api/tracking/location/`
  - Depends on assigned nurse journey state

- `POST /api/visit-notes/`
  - Depends on assigned nurse and in-progress/completed visit state
  - Logs medical access

- `POST /api/ratings/`
  - Depends on completed request
  - Triggers reputation recalculation

- `GET /api/ratings/`
  - Uses role-aware selectors

## 11. Celery Workflow Plan

### Required Queues

- `default`
- `notifications`
- `matching`
- `compliance`
- `audit`

### Workflows

#### Offer Expiry

Trigger:

- Request offers sent to nearest 5 nurses.

Task:

- Expire offers after 2 minutes.
- If no acceptance, expand search radius.
- Notify next eligible nurses.

#### Journey Warning

Trigger:

- Request accepted.

Task:

- After 30 minutes, check if journey started.
- If not started, send warning notification.

#### Automatic Cancellation

Trigger:

- Request accepted.

Task:

- After 60 minutes without movement, cancel assignment.
- Notify patient.
- Return request to matching pool.

#### License Monitoring

Schedule:

- Daily.

Task:

- Send reminders 90, 30, and 7 days before expiry.
- Mark expired licenses as `EXPIRED`.
- Set `is_available = False`.

#### Notification Delivery

Trigger:

- Domain events.

Task:

- Deliver push/email/SMS.
- Record delivery status.
- Retry transient failures.

#### Reputation Recalculation

Trigger:

- Rating submitted.
- Request completed.
- Nurse cancellation.

Task:

- Recalculate reputation from ratings, completion rate, response time, and cancellation rate.

## 12. Notification Architecture

### Event Types

- `JOB_ASSIGNED`
- `JOB_ACCEPTED`
- `JOB_WARNING`
- `JOB_CANCELLED`
- `NURSE_EN_ROUTE`
- `NURSE_ARRIVED`
- `VISIT_STARTED`
- `VISIT_COMPLETED`

### Channels

- Push notifications
- Email
- SMS optional

### Design

- Domain services create notification events.
- Notification records are persisted before delivery.
- Celery dispatches delivery asynchronously.
- Delivery adapters isolate provider-specific code.
- Failed deliveries are retried with backoff.
- Critical request notifications are prioritized.

## 13. Audit Logging Architecture

### General Audit Log

Capture:

- Actor user
- Action
- Resource type
- Resource id
- IP address
- User agent
- Timestamp
- Request id/correlation id

Events:

- Registration
- Login
- Logout
- Failed login
- Profile update
- Nurse verification change
- Request creation
- Request acceptance
- Request cancellation
- Admin review actions

### Medical Access Log

Capture every access to protected patient data:

- Actor user
- Patient
- Resource
- Access reason
- IP address
- Timestamp

Protected resources:

- Medical profile fields
- Dependents medical notes
- Emergency contacts after acceptance
- Visit notes

### Immutability

- Audit records are append-only.
- No hard deletes.
- Admins may view logs but not modify protected medical records.

## 14. Security Architecture

### Authentication Security

- Email-only authentication.
- Strong password validators.
- JWT access/refresh split.
- Refresh token rotation.
- Token blacklist on logout.
- Rate limit login, OTP, and registration.
- Audit failed login attempts.

### Authorization Security

- Role-based permissions: `IsPatient`, `IsNurse`, `IsAdmin`.
- Object-level permissions on every healthcare resource.
- Business logic checks use `user.role`.
- Admin role cannot modify protected medical records unless explicitly permitted by compliance workflow.

### Data Protection

- Encrypt sensitive medical fields at rest.
- HTTPS only in production.
- Secure cookies.
- Secure headers.
- No hard delete of medical data.
- Soft delete with `is_deleted` and `deleted_at`.
- Protected data omitted from serializers by default.

### Infrastructure Security

- Secrets from environment variables.
- Production `DEBUG=False`.
- Restricted `ALLOWED_HOSTS`.
- Nginx TLS termination.
- Gunicorn behind Nginx.
- Database not publicly exposed in production.
- Redis not publicly exposed in production.
- Separate production credentials.

### Privacy Rules By Request State

Before acceptance, nurse sees only:

- Patient first name
- Service type
- Approximate location

After acceptance, assigned nurse may see:

- Relevant medical information
- Exact patient location
- Emergency contacts

Other nurses never receive protected patient details.

## 15. Permission Matrix

| Resource/Action | Anonymous | Patient | Nurse | Assigned Nurse | Admin |
|---|---:|---:|---:|---:|---:|
| Register | Yes | N/A | N/A | N/A | Yes |
| Login | Yes | Yes | Yes | Yes | Yes |
| View own patient profile | No | Yes | No | No | Read-only when authorized |
| Edit own patient profile | No | Yes | No | No | No |
| View another patient profile | No | No | No | Limited after assignment | Read-only when authorized |
| View protected medical fields | No | Own only | No | Yes for assigned request | Read-only when authorized |
| Manage dependents | No | Own only | No | No | No |
| Manage emergency contacts | No | Own only | No | Read after acceptance | Read-only when authorized |
| View own nurse profile | No | No | Yes | Yes | Yes |
| Edit own nurse profile | No | No | Yes | Yes | No |
| Verify nurse | No | No | No | No | Yes |
| Update own location | No | Yes | Yes | Yes | No |
| View nearby nurses | No | Yes | No | No | No |
| Create care request | No | Yes | No | No | No |
| List own requests | No | Yes | Yes, assigned/offered only | Yes | Yes |
| Accept request | No | No | Offered nurses only | Offered nurses only | No |
| Start journey | No | No | No | Yes | No |
| Mark arrived | No | No | No | Yes within 100m | No |
| Start visit | No | No | No | Yes within 100m | No |
| Complete visit | No | No | No | Yes | No |
| Add visit notes | No | No | No | Yes | No |
| Rate completed service | No | Yes, own completed request | No | No | No |
| View audit logs | No | No | No | No | Yes |
| Modify audit logs | No | No | No | No | No |

## 16. Testing Strategy

### Test Layers

- Unit tests for services, permissions, selectors, and serializers.
- Integration tests for API endpoints.
- Transaction tests for request acceptance races.
- Celery task tests for delayed workflows.
- Geospatial tests for PostGIS filtering.
- OSRM adapter tests with mocked route responses.
- Security tests for object-level access.
- Privacy tests for serializer data exposure.
- Regression tests for medical access logging.

### Required Coverage Areas

- Email-only authentication.
- JWT login, refresh, logout, blacklist.
- Patient and nurse registration profile creation.
- Nurse verification gates.
- Location freshness rules.
- Busy/offline/location-hidden exclusion.
- Nearby nurse filtering and OSRM response shape.
- Atomic request acceptance.
- Request status transition rules.
- Arrival and visit start 100m validation.
- Protected medical data visibility.
- Audit and medical access log creation.
- Celery offer expiry, warning, cancellation, license monitoring.

### Performance Tests

- Nearby nurse query with spatial index.
- Request list endpoints with `select_related()` and `prefetch_related()`.
- Pagination behavior.
- N+1 query detection.
- Redis caching behavior for high-read endpoints where appropriate.

## 17. Deployment Strategy

### Local Development

- Docker Compose starts the backend API, frontend, PostgreSQL/PostGIS, Redis, Celery, and OSRM when enabled.
- `.env.example` documents all required variables.
- `python backend/manage.py check` must pass.
- Migrations must run.
- Backend API runs on port 8000.
- Frontend development server runs on a separate port, typically 3000 or 5173 depending on the chosen framework.

### Staging

- Mirrors production topology.
- Uses staging secrets.
- Runs migrations before app rollout.
- Runs smoke tests after deployment.
- Uses OSRM staging endpoint or container.
- Enables structured logs and audit log review.

### Production

- Nginx terminates TLS.
- Gunicorn runs Django workers.
- Celery workers run separately.
- Redis and PostgreSQL are private network services.
- PostGIS extension enabled before migrations.
- Database backups are automated.
- Static files collected during image build or release step.
- Health checks monitor API, database, Redis, Celery, and OSRM.
- Logs are centralized with request correlation ids.

### Release Process

1. Run test suite.
2. Build Docker image.
3. Run migrations.
4. Deploy API and workers.
5. Run smoke tests.
6. Verify audit logging.
7. Verify notification delivery.
8. Monitor error rates and queue depth.

## 18. Implementation Phases

### Phase 0: Planning And Architecture

Goal:

- Establish the system blueprint and implementation boundaries.

Deliverables:

- `PLANS.md`
- Confirmed app boundaries
- Confirmed security model
- Confirmed deployment topology

Dependencies:

- `AGENTS.md`

Risks:

- Ambiguous business rules may lead to premature implementation.
- Medical privacy requirements may be under-modeled if not explicit.

Acceptance Criteria:

- Plan covers architecture, phases, ERD, services, permissions, testing, and deployment.
- No application code is introduced in this phase.

### Phase 1: Backend Foundation

Goal:

- Create a production-ready Django backend skeleton.

Deliverables:

- Root repository structure with separate `backend/` and `frontend/` folders
- Django 5 project
- Settings split by environment
- Required Django apps
- Custom email-only user model
- DRF configuration
- Simple JWT configuration
- PostgreSQL/PostGIS configuration
- Celery and Redis configuration
- Backend Dockerfile under `backend/`
- Root Docker Compose orchestration
- Backend README setup instructions
- Root README explaining the `backend/` and `frontend/` split

Dependencies:

- Python 3.12+
- Docker
- PostgreSQL/PostGIS image
- Redis image

Risks:

- Custom user model mistakes are expensive after migrations.
- PostGIS dependencies can fail if system libraries are missing.
- Local and Docker settings can diverge.

Acceptance Criteria:

- Project runs successfully.
- Initial migrations run.
- `docker compose up` works.
- README includes setup instructions.
- No business workflows are implemented.

### Phase 2: Authentication And Identity

Goal:

- Implement secure account creation and JWT authentication.

Deliverables:

- Patient registration
- Nurse registration
- Login
- Refresh
- Logout with blacklist
- Email verification
- Phone OTP verification
- Auth endpoint docs
- Auth tests

Dependencies:

- Phase 1
- Notification adapter placeholder for OTP/email

Risks:

- OTP endpoints may be abused without throttling.
- Role assignment may be exploited if not constrained.
- Email normalization mistakes can allow duplicate accounts.

Acceptance Criteria:

- Users authenticate with email and password only.
- Patients receive patient profiles.
- Nurses receive nurse profiles.
- Unverified accounts cannot access protected workflows.
- Auth events are audited.

### Phase 3: Profiles, Credentials, And Medical Privacy

Goal:

- Implement patient and nurse profile data with privacy protections.

Deliverables:

- Patient profile
- Nurse profile
- Dependents
- Emergency contacts
- Nurse credentials
- Specializations
- Availability slots
- Travel radius
- Encrypted sensitive medical fields
- Medical access logs
- Profile endpoint docs
- Profile tests

Dependencies:

- Phase 2
- Encryption key management decision

Risks:

- Sensitive fields may leak through serializers.
- Admin permissions may overreach.
- Emergency contact minimum rule may block incomplete onboarding if not staged well.

Acceptance Criteria:

- Medical fields are hidden by default.
- Sensitive reads create medical access logs.
- Nurses cannot receive requests before verification.
- Profile APIs enforce object-level permissions.

### Phase 4: Location And Geospatial Foundation

Goal:

- Implement GPS ingestion and geospatial storage.

Deliverables:

- Location update endpoint
- PostGIS point storage
- Spatial indexes
- Location freshness logic
- Busy/location-hidden exclusion rules
- Nearby candidate selectors
- Location endpoint docs
- Geospatial tests

Dependencies:

- Phase 3
- PostGIS extension available

Risks:

- Storing lat/lng separately would violate the spec.
- Stale locations may produce unsafe matches.
- GPS spoofing mitigation may need later hardening.

Acceptance Criteria:

- Locations are stored as geography points.
- Locations older than 15 minutes are marked stale/excluded.
- Busy or hidden nurses are excluded from matching.
- Returning online requires fresh GPS update.

### Phase 5: OSRM And Nurse Matching

Goal:

- Match patients to nearby verified nurses using road-network estimates.

Deliverables:

- OSRM adapter
- Candidate filtering by PostGIS
- Road-distance and ETA calculation
- Nurse ranking service
- Request offer model
- Nearest 5 nurse distribution
- Radius expansion workflow
- Nearby nurses endpoint docs
- Matching tests

Dependencies:

- Phase 4
- OSRM service endpoint/container
- Redis/Celery

Risks:

- OSRM outage can block matching.
- Road-network calls can be slow without batching/caching.
- Straight-line fallback must not be presented as final distance.

Acceptance Criteria:

- Nearby response includes road distance and ETA.
- Only eligible nurses are returned.
- Blocked nurses are excluded.
- Search does not broadcast to all nurses.

### Phase 6: Care Request Lifecycle

Goal:

- Implement request creation, acceptance, journey, arrival, visit start, completion, and cancellation.

Deliverables:

- Care request model
- Status transitions
- Atomic accept endpoint
- Start journey endpoint
- Arrived endpoint
- Start visit endpoint
- Complete endpoint
- Cancel endpoint
- Assignment privacy serializers
- Request endpoint docs
- Lifecycle tests

Dependencies:

- Phase 5

Risks:

- Race conditions during acceptance.
- Invalid state transitions may corrupt workflow.
- Privacy exposure before acceptance.

Acceptance Criteria:

- Only one nurse can accept a request.
- Before acceptance, nurses see only safe request data.
- Assigned nurse can access required data after acceptance.
- Arrival and visit start require distance within 100m.

### Phase 7: Tracking And Visit Notes

Goal:

- Implement real-time journey tracking records and visit documentation.

Deliverables:

- Tracking location endpoint
- En-route location history
- Patient tracking read model
- Visit notes endpoint
- Follow-up schedule support
- Tracking and visit docs
- Tracking and visit tests

Dependencies:

- Phase 6

Risks:

- Excessive location writes may pressure the database.
- Visit notes contain sensitive medical data.
- Patients must not see unrelated nurse tracking.

Acceptance Criteria:

- Assigned nurse can send updates every 30-60 seconds.
- Patient can track assigned nurse progress.
- Visit notes are accessible only to authorized users.
- Medical access is logged.

### Phase 8: Celery Automation

Goal:

- Implement delayed and scheduled healthcare workflows.

Deliverables:

- Offer expiry task
- Journey warning task
- Auto-cancellation task
- License expiry reminder task
- Reputation recalculation task
- Notification dispatch tasks
- Celery tests

Dependencies:

- Phase 6
- Phase 7
- Redis

Risks:

- Duplicate task execution can create duplicate notifications.
- Clock drift can affect delayed workflows.
- Auto-cancellation must not cancel active visits.

Acceptance Criteria:

- Offers expire after 2 minutes.
- Warning sends after 30 minutes without journey start.
- Request auto-cancels after 60 minutes without movement.
- Expired licenses disable nurse availability.

### Phase 9: Ratings, Reputation, Favorites, And Blocking

Goal:

- Implement patient feedback and nurse preference controls.

Deliverables:

- Ratings endpoint
- Reputation score calculation
- Favorites
- Blocking
- Rating endpoint docs
- Tests

Dependencies:

- Phase 6

Risks:

- Patients may rate incomplete visits.
- Reputation formulas may be gamed.
- Blocking must be enforced during matching.

Acceptance Criteria:

- Patients can rate only completed services.
- Ratings are 1-5 stars.
- Blocked nurses never receive future requests from that patient.
- Reputation updates after relevant events.

### Phase 10: Notifications

Goal:

- Implement reliable event-driven notification delivery.

Deliverables:

- Notification model
- Event creation service
- Push/email/SMS adapters
- Delivery status tracking
- Retry logic
- Notification tests

Dependencies:

- Phase 8
- Provider credentials for production channels

Risks:

- Provider outages.
- Duplicate notifications.
- Sensitive content leakage in notification payloads.

Acceptance Criteria:

- Required notification types are supported.
- Delivery attempts are persisted.
- Sensitive medical data is never included in notification bodies.

### Phase 11: Audit, Compliance, And Hardening

Goal:

- Finalize healthcare-grade auditability and security controls.

Deliverables:

- Audit log APIs for admins
- Medical access log APIs for admins
- Rate limiting
- Secure headers
- Soft delete coverage
- Security tests
- Compliance review checklist

Dependencies:

- All previous phases

Risks:

- Audit logs may expose sensitive data if overly verbose.
- Admin access can become too broad.
- Soft delete behavior can break query assumptions.

Acceptance Criteria:

- Sensitive actions generate audit logs.
- Medical data reads generate medical access logs.
- Protected medical records are never hard-deleted.
- Unauthorized access attempts are denied and tested.

### Phase 12: Production Deployment And Observability

Goal:

- Prepare the system for production operation.

Deliverables:

- Production Docker configuration
- Nginx configuration
- Gunicorn configuration
- Health checks
- Backup strategy
- Logging and monitoring
- Deployment runbook
- Smoke tests

Dependencies:

- Phase 11
- Production infrastructure
- TLS certificates
- Secret management

Risks:

- Missing health checks can hide failed workers.
- Database migrations can be unsafe without rollout discipline.
- Public Redis/PostgreSQL exposure would be severe.

Acceptance Criteria:

- API runs behind Nginx/Gunicorn.
- Celery workers are monitored.
- PostgreSQL/PostGIS and Redis are private.
- Deployment runbook is complete.
- Smoke tests pass after deployment.

## 19. Documentation Plan

Every endpoint must have one dedicated markdown file in `backend/api_docs/`.

Each document must include:

- Purpose
- Endpoint URL
- HTTP method
- Authentication
- Permissions
- Request schema
- Response schema
- Error responses
- Business rules

Documentation is required in the same phase as endpoint implementation.

## 20. Definition Of Done

The platform is complete when:

- Patients can register and request care.
- Nurses can register and verify NCK licenses.
- GPS locations update from frontend devices.
- Patients discover nurses within 100km.
- Distance and ETA use road-network calculations.
- Busy nurses can hide their location.
- Returning nurses update fresh GPS coordinates.
- Nurses accept requests safely without race conditions.
- Journey tracking works in real time.
- Delayed nurses receive warnings.
- Requests auto-cancel after inactivity.
- Medical information remains protected.
- Every endpoint has matching documentation in `backend/api_docs/`.
- All endpoints are tested.
- Audit logs are generated for sensitive actions.
- Healthcare privacy rules are enforced.
