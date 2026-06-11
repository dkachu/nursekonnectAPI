import type { LabelHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Label({ className, ...props }: LabelHTMLAttributes<HTMLLabelElement>): ReactNode {
  return <label className={cn("text-sm font-medium leading-none", className)} {...props} />;
}
