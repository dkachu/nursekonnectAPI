import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Coordinates } from "@/types";

export function TrackingStatusCard({
  coordinates,
}: {
  coordinates: Coordinates | null;
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Location Status</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        {coordinates
          ? `${coordinates.latitude}, ${coordinates.longitude}`
          : "No GPS location submitted."}
      </CardContent>
    </Card>
  );
}
