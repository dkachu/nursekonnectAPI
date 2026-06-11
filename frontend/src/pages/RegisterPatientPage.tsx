import type { ReactNode } from "react";
import { RegistrationForm } from "@/pages/RegistrationForm";

export function RegisterPatientPage(): ReactNode {
  return <RegistrationForm role="PATIENT" title="Create Patient Account" />;
}
