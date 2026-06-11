# AGENTS.md

## NurseKonnect REST API — Production-Ready Backend Specification

### Overview

NurseKonnect is a Home-Based Care platform that connects patients with licensed nurses across Kenya.

Patients can request healthcare services from nearby verified nurses, track nurse arrival in real time, receive care at home, and maintain secure medical records.

The backend must be designed as a secure, scalable, API-first healthcare platform using Django REST Framework.

---

# Technology Stack

- Python 3.12+
- Django 5+
- Django REST Framework
- PostgreSQL
- PostGIS
- Redis
- Celery
- JWT Authentication
- Docker
- Nginx
- Gunicorn

---

# Architecture Principles

1. API-first architecture
2. Healthcare-grade security
3. Privacy by default
4. Mobile-first design
5. Geospatial nurse matching
6. Horizontal scalability
7. Auditability
8. Minimal but production-ready implementation

---

# Mandatory Documentation Rule

Every endpoint MUST have a dedicated markdown file under:

```text
/api_docs/
```

Example:

```text
api_docs/
├── auth_register.md
├── auth_login.md
├── patient_profile.md
├── nurse_profile.md
├── nearby_nurses.md
├── create_request.md
├── accept_request.md
├── start_journey.md
├── complete_visit.md
└── ratings.md
```

Each file must contain:

- Purpose
- Endpoint URL
- HTTP Method
- Authentication
- Permissions
- Request Schema
- Response Schema
- Error Responses
- Business Rules

---

# User Types

## Patient

Can:

- Register
- Login
- Manage profile
- Create care requests
- View nearby nurses
- Track assigned nurse
- View visit history
- Save favorite nurses
- Rate completed services

Cannot:

- Access other patient records

---

## Nurse

Can:

- Register
- Upload credentials
- Manage availability
- Receive requests
- Accept requests
- Track journeys
- Complete visits
- Add visit notes

Must:

- Have verified NCK license
- Have approved profile

---

## Administrator

Can:

- Verify nurses
- Approve credentials
- Suspend accounts
- Review complaints
- View audit logs
- Monitor active requests

Cannot:

- Modify protected medical records

---

# Authentication

JWT Authentication.

Endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/
POST /api/auth/verify-otp/
POST /api/auth/resend-otp/
```

---

# Patient Model

```python
id
user

first_name
last_name
gender
date_of_birth

national_id

phone_number
phone_verified

email
email_verified

profile_photo

blood_group
allergies
chronic_conditions
current_medications
disabilities
medical_notes

emergency_contact_name
emergency_contact_phone

county
address

current_location

created_at
updated_at
```

---

# Patient Dependents

Patients may request care for:

- Child
- Parent
- Spouse
- Relative

Model:

```python
PatientDependent

id
patient

full_name
date_of_birth
gender

relationship

medical_notes
```

---

# Emergency Contacts

Minimum:

```python
2 emergency contacts
```

Fields:

```python
name
phone_number
relationship
```

---

# Medical Information Protection

The following fields are sensitive:

```python
allergies
chronic_conditions
current_medications
medical_notes
```

Requirements:

- Encrypted at rest
- Encrypted in transit
- Access logged
- Hidden from unauthorized users

---

# Nurse Model

```python
id
user

first_name
last_name
gender
date_of_birth

national_id

phone_number
email

profile_photo

nck_license_number
nck_license_expiry
nck_verification_status

specializations

years_of_experience

bio

county
address

current_location

last_location_update

location_visible

is_available

status

rating

reputation_score

created_at
updated_at
```

---

# Nurse Status

```python
ONLINE
BUSY
OFFLINE
```

---

# Nurse Verification Status

```python
PENDING
UNDER_REVIEW
VERIFIED
REJECTED
EXPIRED
```

---

# Credential Management

Store:

```python
NCK License
National ID
Passport Photo
Academic Certificates
Professional Certificates
```

---

# License Monitoring

Automatic reminders:

```python
90 days before expiry
30 days before expiry
7 days before expiry
```

Expired licenses:

```python
is_available = False
```

---

# Nurse Specializations

```python
GENERAL_NURSING
WOUND_CARE
GERIATRIC_CARE
PALLIATIVE_CARE
PEDIATRIC_CARE
MIDWIFERY
MENTAL_HEALTH
ICU_CARE
POST_SURGICAL_CARE
CHRONIC_DISEASE_SUPPORT
```

Many-to-many relationship.

---

# Availability Scheduling

Nurses configure:

```python
day_of_week
start_time
end_time
```

Only nurses currently on shift receive requests.

---

# Maximum Travel Radius

Each nurse configures:

```python
10km
20km
50km
100km
```

No requests outside configured radius.

---

# Location Management

## Source

Location is obtained ONLY from browser/mobile GPS.

Frontend submits:

```json
{
  "latitude": -1.286389,
  "longitude": 36.817223
}
```

Backend stores latest location.

---

# Geographic Storage

Use:

```python
PointField(
    geography=True,
    srid=4326
)
```

Never store latitude and longitude separately for matching.

---

# Location Freshness

```python
MAX_LOCATION_AGE = 15 minutes
```

Locations older than 15 minutes:

```python
location_stale = True
```

Excluded from matching.

---

# Busy Nurse Logic

When:

```python
status = BUSY
```

or

```python
location_visible = False
```

The nurse:

- Does not appear in searches
- Receives no requests
- Is excluded from matching

Last location remains stored.

---

# Returning Online

When:

```python
status = ONLINE
location_visible = True
```

Frontend must submit fresh GPS coordinates.

Backend updates:

```python
current_location
last_location_update
```

---

# Nearby Nurse Matching

Patient can only see nurses that satisfy:

```python
status = ONLINE
is_available = True
location_visible = True
nck_verification_status = VERIFIED
distance <= 100km
```

---

# Distance Calculation

Must use:

```python
PostGIS
```

and

```python
OSRM
```

for road-network routing.

Never use straight-line distance.

---

# Uber/Bolt Style Response

```json
{
  "distance_km": 12.4,
  "estimated_travel_time": 18
}
```

Travel time should resemble Uber/Bolt estimates in Kenya.

---

# Care Request Model

```python
id

patient

dependent

service_type

priority

description

location

requested_time

status

assigned_nurse

created_at
updated_at
```

---

# Priority Levels

```python
NORMAL
URGENT
CRITICAL
```

Critical requests receive higher priority.

---

# Service Types

```python
GENERAL_NURSING
WOUND_CARE
ELDERLY_CARE
PALLIATIVE_CARE
POST_SURGERY_CARE
MATERNITY_CARE
CHRONIC_DISEASE_SUPPORT
```

---

# Request Statuses

```python
PENDING

ACCEPTED

PREPARING

NURSE_EN_ROUTE

ARRIVED

IN_PROGRESS

COMPLETED

CANCELLED

EXPIRED
```

---

# Nurse Matching Algorithm

Rank nurses by:

1. Availability
2. Distance
3. Specialization Match
4. Reputation Score
5. Response Speed

---

# Request Distribution

Notify:

```python
Nearest 5 eligible nurses
```

If nobody accepts:

Expand search radius gradually.

Do NOT broadcast to all nurses.

---

# Acceptance Rules

Only one nurse may own a request.

Use:

```python
transaction.atomic()
```

to prevent race conditions.

---

# Privacy Rules

Before acceptance, nurse may see ONLY:

```python
first_name
service_type
approximate_location
```

Nurse must NOT see:

```python
allergies
medical_history
full_address
contacts
```

---

# After Acceptance

Assigned nurse may access:

- Relevant medical information
- Exact patient location
- Emergency contacts

No other nurse may access this data.

---

# Nurse Response Window

A request offer expires after:

```python
2 minutes
```

and is offered to the next nurse.

---

# Journey Management

After acceptance:

Nurse must start journey within:

```python
30 minutes
```

---

# Warning Logic

After:

```python
30 minutes
```

without journey start:

```python
Send warning
```

---

# Automatic Cancellation

After:

```python
60 minutes
```

without movement:

```python
Cancel request
Remove assignment
Notify patient
Return request to matching pool
```

---

# GPS Tracking

While en route:

Frontend sends location updates every:

```python
30-60 seconds
```

Store:

```python
nurse
location
timestamp
```

Patient can track progress.

---

# Arrival Verification

Nurse cannot mark:

```python
ARRIVED
```

unless within:

```python
100 meters
```

of patient location.

---

# Visit Start Validation

Nurse cannot begin visit unless:

```python
distance <= 100m
```

---

# Visit Notes

Assigned nurse records:

```python
vitals

observations

medication_given

recommendations

follow_up_required
```

---

# Follow-Up Visits

Supported schedules:

```python
1 Day
3 Days
1 Week
2 Weeks
1 Month
```

---

# Nurse Cancellation Logic

If nurse:

```python
Cancels
Goes Offline
Fails To Move
```

System:

```python
Unassign Nurse
Notify Patient
Reassign Request
```

---

# Patient Cancellation Logic

Before acceptance:

```python
Free cancellation
```

After nurse begins journey:

```python
Potential cancellation fee
```

Future payment module.

---

# Favorites

Patients can save nurses.

Model:

```python
PatientFavoriteNurse
```

---

# Blocking

Patients may block nurses.

Reasons:

```python
Poor Service
Harassment
Misconduct
```

Blocked nurses never receive future requests from that patient.

---

# Ratings

```python
1-5 Stars
```

Fields:

```python
patient
nurse
rating
comment
```

---

# Reputation Score

Calculated from:

```python
Ratings
Completion Rate
Response Time
Cancellation Rate
```

---

# Notifications

Support:

```python
JOB_ASSIGNED

JOB_ACCEPTED

JOB_WARNING

JOB_CANCELLED

NURSE_EN_ROUTE

NURSE_ARRIVED

VISIT_STARTED

VISIT_COMPLETED
```

Delivery:

- Push Notifications
- Email
- SMS (Optional)

---

# Audit Logs

Track:

```python
user
action
resource
ip_address
timestamp
```

---

# Medical Access Logs

Track every access to protected data.

```python
user
patient
resource
timestamp
ip_address
```

---

# Data Retention

Never hard-delete medical data.

Use:

```python
is_deleted
deleted_at
```

---

# Security Requirements

Mandatory:

- JWT Authentication
- RBAC Permissions
- HTTPS Only
- Audit Logging
- Rate Limiting
- Secure Headers
- Encrypted Medical Data
- Soft Deletes
- Input Validation
- Object-Level Permissions

Permissions:

```python
IsAuthenticated
IsPatient
IsNurse
IsAdmin
```

---

# Required Django Apps

```text
accounts/
patients/
nurses/
requests/
tracking/
visits/
ratings/
notifications/
audit_logs/
```

---

# Required Endpoints

```text
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
POST   /api/auth/refresh/
POST   /api/auth/verify-otp/

GET    /api/patient/profile/
PATCH  /api/patient/profile/

GET    /api/nurse/profile/
PATCH  /api/nurse/profile/

POST   /api/location/update/

GET    /api/nurses/nearby/

POST   /api/requests/
GET    /api/requests/
GET    /api/requests/{id}/

POST   /api/requests/{id}/accept/
POST   /api/requests/{id}/start-journey/
POST   /api/requests/{id}/arrived/
POST   /api/requests/{id}/start-visit/
POST   /api/requests/{id}/complete/
POST   /api/requests/{id}/cancel/

POST   /api/tracking/location/

POST   /api/visit-notes/

POST   /api/ratings/
GET    /api/ratings/
```

---

# Performance Requirements

Mandatory:

- Prevent N+1 queries
- select_related()
- prefetch_related()
- Database indexes
- Spatial indexes
- Pagination
- Atomic transactions
- Query optimization
- Redis caching

---

# Definition of Done

The API is complete when:

1. Patients can register and request care.
2. Nurses can register and verify NCK licenses.
3. GPS locations update from frontend devices.
4. Patients discover nurses within 100km.
5. Distance and ETA use road-network calculations.
6. Busy nurses can hide their location.
7. Returning nurses update fresh GPS coordinates.
8. Nurses accept requests safely without race conditions.
9. Journey tracking works in real time.
10. Delayed nurses receive warnings.
11. Requests auto-cancel after inactivity.
12. Medical information remains protected.
13. Every endpoint has matching documentation in `/api_docs`.
14. All endpoints are tested.
15. Audit logs are generated for sensitive actions.
16. Healthcare privacy rules are enforced.

---

# Golden Rule

Patient medical information is hidden by default.

Only:

- The patient
- The assigned nurse
- Authorized administrators

may access protected healthcare information.

Every model, serializer, permission class, endpoint, task, and business rule must enforce this principle.



# Authentication & User Architecture

## User Authentication Strategy

NurseKonnect MUST use email-based authentication.

Users authenticate using:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

The platform MUST NOT use usernames.

---

## Custom User Model

The system shall use a custom Django User model built on:

```python
AbstractBaseUser
PermissionsMixin
```

Example structure:

```python
id

email

first_name
last_name

role

is_active
is_staff
is_superuser

email_verified
phone_verified

created_at
updated_at
```

---

## USERNAME_FIELD

```python
USERNAME_FIELD = "email"

REQUIRED_FIELDS = []
```

---

## Email Requirements

```python
email = models.EmailField(
    unique=True,
    db_index=True
)
```

Requirements:

- Unique
- Indexed
- Normalized before save
- Required during registration

---

## Roles

The system supports:

```python
PATIENT
NURSE
ADMIN
```

Example:

```python
class UserRole(models.TextChoices):
    PATIENT = "PATIENT"
    NURSE = "NURSE"
    ADMIN = "ADMIN"
```

---

## Custom User Manager

The custom manager must implement:

```python
create_user()

create_superuser()
```

Requirements:

- Normalize email
- Validate required email
- Hash passwords securely
- Set appropriate permissions

---

# Profile Architecture

Use a single User model and separate profile models.

```text
User
│
├── PatientProfile (OneToOne)
│
└── NurseProfile (OneToOne)
```

Do NOT create separate authentication systems for patients and nurses.

Authentication is centralized through the User model.

---

# Patient Profile

The PatientProfile stores patient-specific information.

```python
user

phone_number

national_id

gender
date_of_birth

profile_photo

blood_group

allergies
chronic_conditions
current_medications
disabilities

medical_notes

emergency_contacts

county
address

current_location

created_at
updated_at
```

---

# Nurse Profile

The NurseProfile stores nurse-specific information.

```python
user

phone_number

national_id

gender
date_of_birth

profile_photo

nck_license_number
nck_license_expiry
nck_verification_status

years_of_experience

specializations

bio

county
address

current_location

last_location_update

location_visible

status

is_available

rating
reputation_score

created_at
updated_at
```

---

# Registration Flow

## Patient Registration

```json
{
  "email": "patient@example.com",
  "password": "StrongPassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+254712345678",
  "role": "PATIENT"
}
```

Automatically creates:

```text
User
PatientProfile
```

---

## Nurse Registration

```json
{
  "email": "nurse@example.com",
  "password": "StrongPassword123!",
  "first_name": "Jane",
  "last_name": "Wanjiku",
  "phone_number": "+254712345678",
  "role": "NURSE"
}
```

Automatically creates:

```text
User
NurseProfile
```

Nurse remains unavailable until NCK verification is complete.

---

# Login Flow

Endpoint:

```http
POST /api/auth/login/
```

Request:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

Response:

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "PATIENT"
  }
}
```

---

# Email Verification

New users start with:

```python
email_verified = False
```

Users must verify their email before accessing protected functionality.

Supported methods:

- Verification Link
- OTP Verification

Recommended:

```python
Verification Link + OTP
```

After successful verification:

```python
email_verified = True
```

---

# Phone Verification

Store:

```python
phone_number
phone_verified
```

Use SMS OTP verification.

Supported format:

```python
+254712345678
```

(E.164 format)

After successful verification:

```python
phone_verified = True
```

---

# Account Activation Rules

Patient accounts require:

```python
email_verified = True
phone_verified = True
```

before requesting care.

---

Nurse accounts require:

```python
email_verified = True
phone_verified = True
nck_verification_status = VERIFIED
```

before receiving requests.

---

# JWT Authentication

Use:

```python
djangorestframework-simplejwt
```

Endpoints:

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/
POST /api/auth/verify-email/
POST /api/auth/verify-phone/
POST /api/auth/resend-email-verification/
POST /api/auth/resend-phone-otp/
```

---

# Permission Architecture

Never determine user types using:

```python
user.is_staff
```

for business logic.

Instead use:

```python
user.role
```

Example:

```python
if request.user.role == UserRole.NURSE:
```

---

# Required Permission Classes

```python
IsAuthenticated

IsPatient

IsNurse

IsAdmin
```

Object-level permissions must be enforced for all healthcare data.

---

# Security Requirements

Authentication subsystem must include:

- JWT Authentication
- Password Hashing
- Email Verification
- Phone Verification
- Rate Limiting
- Secure Headers
- HTTPS Only
- Audit Logging
- Failed Login Monitoring
- Token Blacklisting
- Object-Level Permissions

---

# Healthcare Privacy Rule

Authentication and authorization must enforce:

```text
Patient medical information is hidden by default.

Only:

- The patient
- The assigned nurse
- Authorized administrators

may access protected healthcare information.
```