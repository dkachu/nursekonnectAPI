import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Separator({ className, ...props }: HTMLAttributes<HTMLDivElement>): ReactNode {
  return <div className={cn("h-px w-full bg-border", className)} role="separator" {...props} />;
}
