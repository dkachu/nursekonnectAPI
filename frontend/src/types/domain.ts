import type { AuthUser, UserRole } from "@/types/auth";

export type Gender = "MALE" | "FEMALE" | "OTHER";
export type NurseStatus = "ONLINE" | "BUSY" | "OFFLINE";
export type VerificationStatus = "PENDING" | "UNDER_REVIEW" | "VERIFIED" | "REJECTED" | "EXPIRED";
export type CareRequestStatus =
  | "PENDING"
  | "ACCEPTED"
  | "PREPARING"
  | "NURSE_EN_ROUTE"
  | "ARRIVED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "CANCELLED"
  | "EXPIRED";
export type CarePriority = "NORMAL" | "URGENT" | "CRITICAL";
export enum NotificationEventType {
  JOB_ASSIGNED = "JOB_ASSIGNED",
  JOB_ACCEPTED = "JOB_ACCEPTED",
  JOB_WARNING = "JOB_WARNING",
  JOB_CANCELLED = "JOB_CANCELLED",
  NURSE_EN_ROUTE = "NURSE_EN_ROUTE",
  NURSE_ARRIVED = "NURSE_ARRIVED",
  VISIT_STARTED = "VISIT_STARTED",
  VISIT_COMPLETED = "VISIT_COMPLETED",
}

export type NotificationType = `${NotificationEventType}`;

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export type LocationPayload = Coordinates;

export interface PatientProfile {
  id: number;
  user?: AuthUser;
  email?: string;
  first_name?: string;
  last_name?: string;
  phone_number: string;
  national_id?: string;
  gender?: Gender;
  date_of_birth?: string;
  blood_group?: string;
  allergies?: string;
  chronic_conditions?: string;
  current_medications?: string;
  disabilities?: string;
  medical_notes?: string;
  county?: string;
  address?: string;
  phone_verified?: boolean;
  email_verified?: boolean;
}

export type PatientProfilePatch = Partial<Omit<PatientProfile, "id" | "user">>;

export interface MedicalInformation {
  patient: number;
  allergies?: string;
  chronic_conditions?: string;
  current_medications?: string;
  medical_notes?: string;
  disabilities?: string;
}

export interface EmergencyContact {
  id: number;
  name: string;
  phone_number: string;
  relationship: string;
}

export type EmergencyContactPayload = Omit<EmergencyContact, "id">;

export interface Dependent {
  id: number;
  full_name: string;
  date_of_birth: string;
  gender: Gender;
  relationship: string;
  medical_notes?: string;
}

export type DependentPayload = Omit<Dependent, "id">;

export interface NurseProfile {
  id: number;
  user?: AuthUser;
  email?: string;
  first_name?: string;
  last_name?: string;
  phone_number: string;
  national_id?: string;
  gender?: Gender;
  date_of_birth?: string;
  nck_license_number?: string;
  nck_license_expiry?: string;
  nck_verification_status: VerificationStatus;
  years_of_experience?: number;
  bio?: string;
  county?: string;
  address?: string;
  specializations?: Specialization[];
  location_visible: boolean;
  is_available: boolean;
  status: NurseStatus;
  travel_radius_km?: number;
  rating?: string;
  reputation_score?: string;
}

export interface NearbyNurse {
  id: number;
  first_name?: string;
  last_name?: string;
  specializations?: string[];
  rating?: string;
  reputation_score?: string;
  distance_km?: number;
  estimated_travel_time?: number;
  is_available?: boolean;
}

export interface Specialization {
  id: number;
  code: string;
  name: string;
}

export interface NurseCredential {
  id: number;
  credential_type: string;
  image: string;
  verification_status: VerificationStatus;
  reviewed_by?: number | null;
  reviewed_at?: string | null;
  review_notes?: string;
}

export interface AvailabilitySlot {
  id: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
}

export interface CareRequest {
  id: number;
  patient: number;
  dependent?: number | null;
  service_type: string;
  priority: CarePriority;
  description: string;
  requested_time?: string;
  status: CareRequestStatus;
  assigned_nurse?: number | null;
  assigned_nurse_id?: number | null;
  assigned_nurse_name?: string;
  patient_first_name?: string;
  patient_last_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CareRequestPayload {
  dependent_id?: number | null;
  service_type: string;
  priority: CarePriority;
  description: string;
  location: Coordinates;
  requested_time?: string;
}

export interface TrackingLocation {
  id: number;
  nurse?: number;
  care_request_id?: number;
  latitude?: number;
  longitude?: number;
  recorded_at: string;
  timestamp?: string;
  location_stale?: boolean;
}

export type TrackingLocationPayload = LocationPayload;

export interface VisitNote {
  id: number;
  care_request_id: number;
  patient_id: number;
  nurse_id: number;
  nurse_name?: string;
  vitals?: string;
  observations?: string;
  medication_given?: string;
  recommendations?: string;
  follow_up_required: boolean;
  follow_up_schedule?: string;
  created_at: string;
  updated_at: string;
}

export interface VisitNotePayload {
  care_request_id: number;
  vitals?: string;
  observations?: string;
  medication_given?: string;
  recommendations?: string;
  follow_up_required?: boolean;
  follow_up_schedule?: string;
}

export interface Rating {
  id: number;
  patient_id: number;
  nurse_id: number;
  nurse_name?: string;
  care_request_id?: number;
  rating: number;
  comment?: string;
  created_at: string;
}

export interface RatingPayload {
  care_request_id: number;
  rating: number;
  comment?: string;
}

export interface Notification {
  id: number;
  user: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  results: Notification[];
  count?: number;
  next?: string | null;
  previous?: string | null;
}

export interface UnreadNotificationCount {
  unread_count: number;
}

export interface MarkAllNotificationsReadResponse {
  updated_count: number;
}

export interface AdminNurseVerificationPayload {
  nck_verification_status: VerificationStatus;
  nck_license_number?: string;
  nck_license_expiry?: string;
}

export interface CredentialReviewPayload {
  verification_status: VerificationStatus;
  review_notes?: string;
}

export interface PermissionSet {
  canViewMedicalData: boolean;
  canManageRequests: boolean;
  canVerifyNurses: boolean;
  role: UserRole | null;
}
