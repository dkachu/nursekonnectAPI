import { zodResolver } from "@hookform/resolvers/zod";
import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { getApiErrorMessage } from "@/api/client";
import { useAuth } from "@/auth/useAuth";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "@/hooks/useAuthMutations";
import type { UserRole } from "@/types/auth";
import { kenyanPhoneNumberSchema } from "@/types/validation";

const registrationSchema = z.object({
  first_name: z.string().min(2, "First name is required."),
  last_name: z.string().min(2, "Last name is required."),
  phone_number: kenyanPhoneNumberSchema,
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(8, "Password must be at least 8 characters."),
});

type RegistrationFormValues = z.infer<typeof registrationSchema>;

interface RegistrationFormProps {
  role: Extract<UserRole, "PATIENT" | "NURSE">;
  title: string;
}

export function RegistrationForm({ role, title }: RegistrationFormProps): ReactNode {
  const navigate = useNavigate();
  const { login } = useAuth();
  const registerMutation = useRegister();
  const [error, setError] = useState<string | null>(null);
  const {
    formState: { errors, isSubmitting },
    handleSubmit,
    register,
  } = useForm<RegistrationFormValues>({ resolver: zodResolver(registrationSchema) });

  async function onSubmit(values: RegistrationFormValues): Promise<void> {
    setError(null);
    try {
      await registerMutation.mutateAsync({ ...values, role });
      await login(values.email, values.password);
      void navigate("/verify");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-220px)] max-w-xl flex-col justify-center px-4 py-12">
      <Card>
        <CardHeader className="items-center text-center">
          <Logo />
          <CardTitle className="mt-4">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-4 sm:grid-cols-2"
            onSubmit={(event) => void handleSubmit(onSubmit)(event)}
          >
            <div className="space-y-2">
              <Label htmlFor="first_name">First name</Label>
              <Input id="first_name" {...register("first_name")} />
              {errors.first_name ? (
                <p className="text-sm text-destructive">{errors.first_name.message}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Last name</Label>
              <Input id="last_name" {...register("last_name")} />
              {errors.last_name ? (
                <p className="text-sm text-destructive">{errors.last_name.message}</p>
              ) : null}
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="phone_number">Phone number</Label>
              <Input
                id="phone_number"
                type="tel"
                placeholder="+254712345678"
                {...register("phone_number")}
              />
              {errors.phone_number ? (
                <p className="text-sm text-destructive">{errors.phone_number.message}</p>
              ) : null}
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" autoComplete="email" {...register("email")} />
              {errors.email ? (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              ) : null}
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                {...register("password")}
              />
              {errors.password ? (
                <p className="text-sm text-destructive">{errors.password.message}</p>
              ) : null}
            </div>
            {error ? <p className="text-sm text-destructive sm:col-span-2">{error}</p> : null}
            <Button
              className="sm:col-span-2"
              type="submit"
              disabled={isSubmitting || registerMutation.isPending}
            >
              {isSubmitting || registerMutation.isPending ? "Creating account" : "Create account"}
            </Button>
          </form>
          <p className="mt-5 text-center text-sm text-muted-foreground">
            Already registered?{" "}
            <Link className="font-medium text-foreground" to="/login">
              Login
            </Link>
          </p>
        </CardContent>
      </Card>
    </section>
  );
}
