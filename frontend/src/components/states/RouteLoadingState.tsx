import type { ReactNode } from "react";
import { LoadingState } from "@/components/states/LoadingState";

export function RouteLoadingState(): ReactNode {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <LoadingState />
    </div>
  );
}
