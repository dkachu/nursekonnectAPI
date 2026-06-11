import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CareRequest } from "@/types";

export function RequestStatusCard({ request }: { request: CareRequest }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{request.service_type}</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-between text-sm">
        <Badge variant="neutral">{request.status}</Badge>
        <span className="text-muted-foreground">{request.priority}</span>
      </CardContent>
    </Card>
  );
}
