import { z } from "zod";

export const kenyanPhoneNumberSchema = z
  .string()
  .regex(/^\+254\d{9}$/, "Use Kenyan E.164 format, for example +254712345678.");

export const otpCodeSchema = z.string().regex(/^\d{6}$/, "Enter the 6-digit OTP code.");
