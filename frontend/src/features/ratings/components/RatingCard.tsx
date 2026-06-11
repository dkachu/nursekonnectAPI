import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Rating } from "@/types";

export function RatingCard({ rating }: { rating: Rating }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{rating.rating}/5 Stars</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        {rating.comment ?? "No comment provided."}
      </CardContent>
    </Card>
  );
}
