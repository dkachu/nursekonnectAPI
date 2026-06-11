/**
 * Generated from ../OPENAPI.yaml during the final healthcare production audit.
 * Keep this file synchronized with the backend OpenAPI schema before releases.
 */

export type OpenApiUserRole = "PATIENT" | "NURSE" | "ADMIN";
export type OpenApiRegisterRole = "PATIENT" | "NURSE";
export type OpenApiOTPPurpose = "EMAIL" | "PHONE";

export interface OpenApiRegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  role: OpenApiRegisterRole;
}

export interface OpenApiLoginRequest {
  email: string;
  password: string;
}

export type OpenApiRefreshRequest = Record<string, never>;

export interface OpenApiOTPVerifyRequest {
  purpose: OpenApiOTPPurpose;
  code: string;
}

export interface OpenApiOTPResendRequest {
  purpose: OpenApiOTPPurpose;
}

export interface OpenApiUser {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role: OpenApiUserRole;
  email_verified?: boolean;
  phone_verified?: boolean;
  profile?: Record<string, unknown> | null;
}

export interface OpenApiUserEnvelope {
  user: OpenApiUser;
}

export interface OpenApiLoginResponse {
  access: string;
  user: OpenApiUser;
}

export interface OpenApiRefreshResponse {
  access: string;
}

export interface OpenApiLocationUpdate {
  latitude: number;
  longitude: number;
}

export interface OpenApiNearbyNurseQuery {
  specialization?: string;
  limit?: number;
}

export interface OpenApiNurseStatusRequest {
  status: "ONLINE" | "BUSY" | "OFFLINE";
  location_visible?: boolean;
  is_available?: boolean;
}

export interface OpenApiNurseProfileSpecializationsRequest {
  specializations: number[];
}

export interface OpenApiPatientProfile {
  id: number;
  email?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  blood_group?: string;
  allergies?: string;
  chronic_conditions?: string;
  current_medications?: string;
  medical_notes?: string;
}

export interface OpenApiPatientProfilePatch {
  national_id?: string;
  gender?: string;
  date_of_birth?: string;
  blood_group?: string;
  allergies?: string;
  chronic_conditions?: string;
  current_medications?: string;
  disabilities?: string;
  medical_notes?: string;
  county?: string;
  address?: string;
}

export interface OpenApiSchemas {
  RegisterRequest: OpenApiRegisterRequest;
  LoginRequest: OpenApiLoginRequest;
  RefreshRequest: OpenApiRefreshRequest;
  OTPVerifyRequest: OpenApiOTPVerifyRequest;
  OTPResendRequest: OpenApiOTPResendRequest;
  User: OpenApiUser;
  UserEnvelope: OpenApiUserEnvelope;
  LoginResponse: OpenApiLoginResponse;
  RefreshResponse: OpenApiRefreshResponse;
  LocationUpdate: OpenApiLocationUpdate;
  NearbyNurseQuery: OpenApiNearbyNurseQuery;
  NurseStatusRequest: OpenApiNurseStatusRequest;
  NurseProfileSpecializationsRequest: OpenApiNurseProfileSpecializationsRequest;
  PatientProfile: OpenApiPatientProfile;
  PatientProfilePatch: OpenApiPatientProfilePatch;
}

export interface OpenApiPaths {
  "/api/auth/register/": {
    post: { request: OpenApiRegisterRequest; response: OpenApiUserEnvelope };
  };
  "/api/auth/login/": { post: { request: OpenApiLoginRequest; response: OpenApiLoginResponse } };
  "/api/auth/me/": { get: { response: OpenApiUserEnvelope } };
  "/api/auth/refresh/": {
    post: { request: OpenApiRefreshRequest; response: OpenApiRefreshResponse };
  };
  "/api/auth/logout/": { post: { request: OpenApiRefreshRequest; response: void } };
  "/api/auth/verify-otp/": {
    post: { request: OpenApiOTPVerifyRequest; response: OpenApiUserEnvelope };
  };
  "/api/auth/resend-otp/": {
    post: { request: OpenApiOTPResendRequest; response: { expires_at?: string } };
  };
  "/api/location/update/": {
    post: { request: OpenApiLocationUpdate; response: { location_stale?: boolean } };
  };
  "/api/nurses/nearby/": {
    get: { query: OpenApiNearbyNurseQuery; response: unknown[] };
  };
  "/api/nurses/nck-license-status/": {
    get: { response: void };
  };
  "/api/nurse/profile/specializations/": {
    put: { request: OpenApiNurseProfileSpecializationsRequest; response: unknown };
  };
  "/api/nurse/status/": {
    post: { request: OpenApiNurseStatusRequest; response: unknown };
  };
  "/api/tracking/location/": {
    post: { request: OpenApiLocationUpdate; response: unknown };
  };
}
