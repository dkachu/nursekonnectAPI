import { zodResolver } from "@hookform/resolvers/zod";
import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { getApiErrorMessage } from "@/api/client";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useResendOtp, useVerifyOtp } from "@/hooks/useAuthMutations";
import { otpCodeSchema } from "@/types/validation";

const verifySchema = z.object({
  purpose: z.enum(["EMAIL", "PHONE"]),
  code: otpCodeSchema,
});

type VerifyFormValues = z.infer<typeof verifySchema>;

export function VerifyPage(): ReactNode {
  const verifyOtp = useVerifyOtp();
  const resendOtp = useResendOtp();
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const {
    formState: { errors, isSubmitting },
    getValues,
    handleSubmit,
    register,
  } = useForm<VerifyFormValues>({
    resolver: zodResolver(verifySchema),
    defaultValues: { purpose: "EMAIL", code: "" },
  });

  async function onSubmit(values: VerifyFormValues): Promise<void> {
    setError(null);
    setSuccess(null);
    try {
      await verifyOtp.mutateAsync(values);
      setSuccess("Your account verification was accepted.");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    }
  }

  async function onResend(): Promise<void> {
    setError(null);
    setSuccess(null);
    try {
      await resendOtp.mutateAsync({ purpose: getValues("purpose") });
      setSuccess("A new verification code was sent.");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-220px)] max-w-md flex-col justify-center px-4 py-12">
      <Card>
        <CardHeader className="items-center text-center">
          <Logo />
          <CardTitle className="mt-4">Verify Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={(event) => void handleSubmit(onSubmit)(event)}>
            <div className="space-y-2">
              <Label htmlFor="purpose">Verification type</Label>
              <select
                id="purpose"
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                {...register("purpose")}
              >
                <option value="EMAIL">Email</option>
                <option value="PHONE">Phone</option>
              </select>
              {errors.purpose ? (
                <p className="text-sm text-destructive">{errors.purpose.message}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor="otp">Verification code</Label>
              <Input
                id="otp"
                inputMode="numeric"
                placeholder="Enter 6-digit OTP"
                {...register("code")}
              />
              {errors.code ? (
                <p className="text-sm text-destructive">{errors.code.message}</p>
              ) : null}
            </div>
            {success ? <p className="text-sm text-emerald-700">{success}</p> : null}
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
            <Button className="w-full" type="submit" disabled={isSubmitting || verifyOtp.isPending}>
              {verifyOtp.isPending ? "Verifying" : "Verify"}
            </Button>
            <Button
              className="w-full"
              type="button"
              variant="outline"
              onClick={() => void onResend()}
              disabled={resendOtp.isPending}
            >
              {resendOtp.isPending ? "Sending" : "Resend Code"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
