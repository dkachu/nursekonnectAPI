import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { MapPin, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { NearbyNurse } from "@/types";

export function NurseCard({ nurse }: { nurse: NearbyNurse }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle>
              {[nurse.first_name, nurse.last_name].filter(Boolean).join(" ") || "Verified Nurse"}
            </CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              {nurse.specializations?.join(", ") ?? "General Nursing"}
            </p>
          </div>
          <Badge variant={nurse.is_available ? "success" : "neutral"}>
            {nurse.is_available ? "Available" : "Unavailable"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="grid gap-3 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-2">
          <MapPin className="h-4 w-4 text-primary" aria-hidden="true" />
          {nurse.distance_km ?? "—"} km
        </span>
        <span className="inline-flex items-center gap-2">
          <Star className="h-4 w-4 text-primary" aria-hidden="true" />
          {nurse.rating ?? "Not rated"}
        </span>
        <span>ETA: {nurse.estimated_travel_time ?? "—"} minutes</span>
      </CardContent>
      <CardFooter>
        <Button asChild className="w-full">
          <Link to="/requests">Create Care Request</Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
