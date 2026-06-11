import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { VisitNote } from "@/types";

export function VisitNoteCard({ note }: { note: VisitNote }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Visit #{note.id}</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        {note.recommendations ?? "No recommendations recorded."}
      </CardContent>
    </Card>
  );
}
