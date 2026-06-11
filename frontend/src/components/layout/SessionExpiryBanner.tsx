import { useEffect, useState, type ReactNode } from "react";
import { useAuth } from "@/auth/useAuth";
import { Button } from "@/components/ui/button";

const SESSION_WARNING_MS = 14 * 60 * 1000;

export function SessionExpiryBanner(): ReactNode {
  const { isAuthenticated, refreshSession } = useAuth();
  const [showWarning, setShowWarning] = useState(false);
  const visible = isAuthenticated && showWarning;

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const timeout = window.setTimeout(() => setShowWarning(true), SESSION_WARNING_MS);
    return () => window.clearTimeout(timeout);
  }, [isAuthenticated]);

  if (!visible) {
    return null;
  }

  return (
    <div className="border-b border-blue-200 bg-blue-50 px-4 py-2 text-center text-sm text-blue-950">
      Your session may expire soon.
      <Button
        className="ml-3 h-8"
        size="sm"
        variant="outline"
        onClick={() => {
          void refreshSession().then(() => setShowWarning(false));
        }}
      >
        Keep Session Active
      </Button>
    </div>
  );
}
