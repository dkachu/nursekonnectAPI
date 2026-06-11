import { useMutation } from "@tanstack/react-query";
import { authService } from "@/services/auth.service";
import type { AuthUser, OTPResendRequest, OTPVerifyRequest, RegisterRequest } from "@/types";

export function useRegister() {
  return useMutation<AuthUser, Error, RegisterRequest>({
    mutationFn: (payload) => authService.register(payload),
  });
}

export function useVerifyOtp() {
  return useMutation<AuthUser, Error, OTPVerifyRequest>({
    mutationFn: (payload) => authService.verifyOtp(payload),
  });
}

export function useResendOtp() {
  return useMutation<{ expires_at?: string }, Error, OTPResendRequest>({
    mutationFn: (payload) => authService.resendOtp(payload),
  });
}
