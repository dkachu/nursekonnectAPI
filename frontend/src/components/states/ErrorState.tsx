import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title?: string;
  message: string;
  retryLabel?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  retryLabel = "Try Again",
  onRetry,
}: ErrorStateProps): ReactNode {
  return (
    <Card>
      <CardContent className="flex min-h-40 flex-col items-center justify-center p-8 text-center">
        <h2 className="text-base font-semibold">{title}</h2>
        <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">{message}</p>
        {onRetry ? (
          <div className="mt-5">
            <Button variant="outline" onClick={onRetry}>
              {retryLabel}
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
