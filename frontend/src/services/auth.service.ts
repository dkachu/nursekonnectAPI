import { authApi } from "@/api/auth.api";
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  OTPResendRequest,
  OTPVerifyRequest,
  RefreshResponse,
  RegisterRequest,
} from "@/types";

export class AuthService {
  async register(payload: RegisterRequest): Promise<AuthUser> {
    return authApi.register(payload);
  }

  async login(payload: LoginRequest): Promise<LoginResponse> {
    return authApi.login(payload);
  }

  async refreshSession(): Promise<RefreshResponse> {
    return authApi.refresh();
  }

  async restoreSession(): Promise<AuthUser> {
    await authApi.refresh();
    return authApi.me();
  }

  async getCurrentUser(): Promise<AuthUser> {
    return authApi.me();
  }

  async logout(): Promise<void> {
    await authApi.logout();
  }

  async verifyOtp(payload: OTPVerifyRequest): Promise<AuthUser> {
    return authApi.verifyOtp(payload);
  }

  async resendOtp(payload: OTPResendRequest): Promise<{ expires_at?: string }> {
    return authApi.resendOtp(payload);
  }
}

export const authService = new AuthService();
