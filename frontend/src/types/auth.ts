import type {
  OpenApiLoginRequest,
  OpenApiLoginResponse,
  OpenApiOTPPurpose,
  OpenApiOTPResendRequest,
  OpenApiOTPVerifyRequest,
  OpenApiRefreshRequest,
  OpenApiRefreshResponse,
  OpenApiRegisterRequest,
  OpenApiUser,
  OpenApiUserRole,
} from "@/types/openapi.generated";

export type UserRole = OpenApiUserRole;
export type OTPPurpose = OpenApiOTPPurpose;

export type AuthUser = OpenApiUser;

export type LoginResponse = OpenApiLoginResponse;

export type RefreshResponse = OpenApiRefreshResponse;

export type RegisterRequest = OpenApiRegisterRequest;

export type LoginRequest = OpenApiLoginRequest;

export type RefreshRequest = OpenApiRefreshRequest;

export type OTPVerifyRequest = OpenApiOTPVerifyRequest;

export type OTPResendRequest = OpenApiOTPResendRequest;
