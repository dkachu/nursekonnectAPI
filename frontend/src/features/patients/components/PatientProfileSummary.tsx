import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PatientProfile } from "@/types";

export function PatientProfileSummary({ profile }: { profile: PatientProfile }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Patient Profile</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-2 text-sm">
        <span>{profile.phone_number}</span>
        <span className="text-muted-foreground">{profile.county ?? "County not set"}</span>
      </CardContent>
    </Card>
  );
}
