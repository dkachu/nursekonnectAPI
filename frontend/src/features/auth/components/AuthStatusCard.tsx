import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AuthUser } from "@/types";

export function AuthStatusCard({ user }: { user: AuthUser | null }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Session</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        {user ? `${user.email} is signed in as ${user.role}.` : "No active session."}
      </CardContent>
    </Card>
  );
}
