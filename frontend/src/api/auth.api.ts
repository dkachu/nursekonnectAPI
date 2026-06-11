import { apiClient, setAuthTokens } from "@/api/client";
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  OTPResendRequest,
  OTPVerifyRequest,
  RefreshResponse,
  RegisterRequest,
} from "@/types";

type UserEnvelope = { user: AuthUser };

function unwrapUser(payload: AuthUser | Partial<UserEnvelope>): AuthUser {
  if ("user" in payload && payload.user) {
    return payload.user;
  }
  return payload as AuthUser;
}

export const authApi = {
  async register(payload: RegisterRequest): Promise<AuthUser> {
    const response = await apiClient.post<AuthUser | Partial<UserEnvelope>>(
      "/api/auth/register/",
      payload,
    );
    return unwrapUser(response.data);
  },

  async login(payload: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>("/api/auth/login/", payload);
    setAuthTokens(response.data);
    return response.data;
  },

  async refresh(): Promise<RefreshResponse> {
    const response = await apiClient.post<RefreshResponse>("/api/auth/refresh/", {});
    setAuthTokens({ access: response.data.access });
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post<void>("/api/auth/logout/", {});
    setAuthTokens(null);
  },

  async me(): Promise<AuthUser> {
    const response = await apiClient.get<AuthUser | Partial<UserEnvelope>>("/api/auth/me/");
    return unwrapUser(response.data);
  },

  async verifyOtp(payload: OTPVerifyRequest): Promise<AuthUser> {
    const response = await apiClient.post<AuthUser | Partial<UserEnvelope>>(
      "/api/auth/verify-otp/",
      payload,
    );
    return unwrapUser(response.data);
  },

  async resendOtp(payload: OTPResendRequest): Promise<{ expires_at?: string }> {
    const response = await apiClient.post<{ expires_at?: string }>(
      "/api/auth/resend-otp/",
      payload,
    );
    return response.data;
  },
};
