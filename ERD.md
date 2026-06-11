# NurseKonnect ERD

## Core Identity

```text
User
  id PK
  email UNIQUE INDEX
  role PATIENT|NURSE|ADMIN
  email_verified
  phone_verified
  is_active
  is_staff
  is_superuser
  created_at
  updated_at

User 1--0..1 PatientProfile
User 1--0..1 NurseProfile
User 1--many AuditLog
User 1--many MedicalAccessLog
User 1--many Notification
```

## Patient Domain

```text
PatientProfile
  id PK
  user_id FK UNIQUE -> User
  phone_number
  national_id
  gender
  date_of_birth
  blood_group
  allergies ENCRYPTED
  chronic_conditions ENCRYPTED
  current_medications ENCRYPTED
  disabilities
  medical_notes ENCRYPTED
  county
  address
  current_location geography(Point, 4326) SPATIAL INDEX
  last_location_update INDEX
  created_at
  updated_at

EmergencyContact
  id PK
  patient_id FK -> PatientProfile INDEX
  name
  phone_number
  relationship
  is_deleted INDEX
  deleted_at INDEX
  created_at
  updated_at

PatientDependent
  id PK
  patient_id FK -> PatientProfile INDEX
  full_name
  date_of_birth
  gender
  relationship
  medical_notes ENCRYPTED
  is_deleted INDEX
  deleted_at INDEX
  created_at
  updated_at

PatientProfile 1--many EmergencyContact
PatientProfile 1--many PatientDependent
```

## Nurse Domain

```text
NurseProfile
  id PK
  user_id FK UNIQUE -> User
  phone_number
  national_id
  nck_license_number INDEX
  nck_license_expiry
  nck_verification_status INDEX
  years_of_experience
  county
  address
  current_location geography(Point, 4326) SPATIAL INDEX
  last_location_update INDEX
  location_visible
  status INDEX
  is_available INDEX
  travel_radius_km INDEX
  rating
  completed_visits_count
  cancelled_visits_count
  average_response_seconds
  reputation_score

NurseSpecialization
  id PK
  code UNIQUE INDEX
  name

NurseCredential
  id PK
  nurse_id FK -> NurseProfile INDEX
  credential_type INDEX
  image
  verification_status INDEX
  reviewed_by_id FK -> User
  reviewed_at
  review_notes

NurseAvailabilitySlot
  id PK
  nurse_id FK -> NurseProfile INDEX
  day_of_week INDEX
  start_time
  end_time

NurseProfile many--many NurseSpecialization
NurseProfile 1--many NurseCredential
NurseProfile 1--many NurseAvailabilitySlot
```

## Care Request, Matching, Tracking, Visits

```text
CareRequest
  id PK
  patient_id FK -> PatientProfile INDEX
  dependent_id FK -> PatientDependent NULL
  service_type
  priority INDEX
  description
  location geography(Point, 4326) SPATIAL INDEX
  requested_time INDEX
  status INDEX
  assigned_nurse_id FK -> NurseProfile NULL INDEX
  accepted_at
  journey_started_at
  arrived_at
  visit_started_at
  completed_at
  cancelled_at
  expired_at
  cancellation_reason
  is_deleted INDEX
  deleted_at INDEX

RequestOffer
  id PK
  care_request_id FK -> CareRequest INDEX
  nurse_id FK -> NurseProfile INDEX
  status INDEX
  radius_km INDEX
  distance_km
  estimated_travel_time
  specialization_match
  rank INDEX
  expires_at INDEX
  notification_id FK -> Notification NULL
  UNIQUE(care_request_id, nurse_id)

TrackingLocation
  id PK
  nurse_id FK -> NurseProfile INDEX
  care_request_id FK -> CareRequest NULL INDEX
  location geography(Point, 4326) SPATIAL INDEX
  recorded_at INDEX

VisitNote
  id PK
  care_request_id FK UNIQUE -> CareRequest
  patient_id FK -> PatientProfile INDEX
  nurse_id FK -> NurseProfile INDEX
  vitals ENCRYPTED
  observations ENCRYPTED
  medication_given ENCRYPTED
  recommendations ENCRYPTED
  follow_up_required INDEX
  follow_up_schedule
  follow_up_due_at INDEX
  is_deleted INDEX
  deleted_at INDEX

CareRequest 1--many RequestOffer
CareRequest 1--many TrackingLocation
CareRequest 1--0..1 VisitNote
NurseProfile 1--many RequestOffer
NurseProfile 1--many TrackingLocation
```

## Ratings, Notifications, Audit

```text
Rating
  id PK
  patient_id FK -> PatientProfile INDEX
  nurse_id FK -> NurseProfile INDEX
  care_request_id FK UNIQUE -> CareRequest
  rating CHECK 1..5 INDEX
  comment
  is_deleted INDEX
  deleted_at INDEX

Notification
  id PK
  recipient_id FK -> User INDEX
  notification_type INDEX
  channel INDEX
  status INDEX
  title
  body
  payload
  resource
  resource_id
  delivered_at
  failed_at
  failure_reason

AuditLog
  id PK
  actor_id FK -> User NULL INDEX
  action INDEX
  resource INDEX
  resource_id INDEX
  ip_address
  metadata
  created_at INDEX

MedicalAccessLog
  id PK
  actor_id FK -> User INDEX
  patient_id FK -> PatientProfile INDEX
  resource INDEX
  resource_id INDEX
  action
  ip_address
  created_at INDEX
```

## Query Optimization Notes

- Role-scoped selectors use `select_related()` for user/profile/request/nurse joins.
- Nurse specialization matching uses `prefetch_related("specializations")`.
- Spatial candidate filtering uses PostGIS `distance_lte` before OSRM routing.
- Matching persists `RequestOffer` rows to avoid full-network broadcasts.
- Protected list endpoints use indexed ownership/status filters.
