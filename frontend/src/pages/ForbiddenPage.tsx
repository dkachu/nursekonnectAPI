import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "@/components/states/EmptyState";
import { Button } from "@/components/ui/button";

export function ForbiddenPage(): ReactNode {
  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <EmptyState
        title="Access Restricted"
        message="Your current role does not have permission to view this page."
        action={
          <Button asChild>
            <Link to="/dashboard">Go to Dashboard</Link>
          </Button>
        }
      />
    </main>
  );
}
