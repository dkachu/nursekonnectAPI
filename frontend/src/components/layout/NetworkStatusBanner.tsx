import type { ReactNode } from "react";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";

export function NetworkStatusBanner(): ReactNode {
  const { online, slowConnection } = useNetworkStatus();

  if (online && !slowConnection) {
    return null;
  }

  return (
    <div className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-sm text-amber-900">
      {online
        ? "Your network appears slow. Location updates and care requests may take longer than usual."
        : "You are offline. Existing screens remain visible, but new care actions require a connection."}
    </div>
  );
}
