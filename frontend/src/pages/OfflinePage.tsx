import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "@/components/states/EmptyState";
import { Button } from "@/components/ui/button";

export function OfflinePage(): ReactNode {
  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <EmptyState
        title="You Are Offline"
        message="Check your connection before submitting care requests, location updates, visit notes, or ratings."
        action={
          <Button asChild variant="outline">
            <Link to="/">Return Home</Link>
          </Button>
        }
      />
    </main>
  );
}
