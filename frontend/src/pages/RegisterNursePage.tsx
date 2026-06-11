import type { ReactNode } from "react";
import { RegistrationForm } from "@/pages/RegistrationForm";

export function RegisterNursePage(): ReactNode {
  return <RegistrationForm role="NURSE" title="Create Nurse Account" />;
}
