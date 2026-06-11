import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "@/components/states/EmptyState";
import { Button } from "@/components/ui/button";

export function NotFoundPage(): ReactNode {
  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <EmptyState
        title="Page Not Found"
        message="The page you requested is unavailable or has moved."
        action={
          <Button asChild>
            <Link to="/">Return Home</Link>
          </Button>
        }
      />
    </main>
  );
}
