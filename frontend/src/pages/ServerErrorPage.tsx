import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "@/components/states/EmptyState";
import { Button } from "@/components/ui/button";

export function ServerErrorPage(): ReactNode {
  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <EmptyState
        title="Service Unavailable"
        message="NurseKonnect could not complete the request. Please retry after confirming the API is available."
        action={
          <Button asChild>
            <Link to="/dashboard">Go to Dashboard</Link>
          </Button>
        }
      />
    </main>
  );
}
