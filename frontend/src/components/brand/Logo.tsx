import type { ReactNode } from "react";
import logoUrl from "@/assets/logo/nursekonnect-logo.svg";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  compact?: boolean;
}

export function Logo({ className, compact = false }: LogoProps): ReactNode {
  return (
    <span className={cn("inline-flex items-center gap-3", className)} aria-label="NurseKonnect">
      <img
        src={logoUrl}
        alt="NurseKonnect"
        className={cn(compact ? "h-9 w-auto max-w-[170px]" : "h-11 w-auto max-w-[220px]")}
      />
    </span>
  );
}
