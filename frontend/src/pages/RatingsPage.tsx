import type { ReactNode } from "react";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { Star } from "lucide-react";
import { useAuth } from "@/auth/useAuth";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RatingCard } from "@/features/ratings/components/RatingCard";
import { useRatings, useSubmitRating } from "@/hooks/useRatings";
import { useRequests } from "@/hooks/useRequests";
import { getUserErrorMessage } from "@/utils/errors";

function formText(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

export function RatingsPage(): ReactNode {
  const { user } = useAuth();
  const { data = [], isLoading, error, refetch } = useRatings();
  const requests = useRequests();
  const submitRating = useSubmitRating();
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const ratedRequestIds = new Set(data.map((rating) => rating.care_request_id));
  const completedRequests = (requests.data ?? []).filter(
    (request) => request.status === "COMPLETED" && !ratedRequestIds.has(request.id),
  );

  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setFormError(null);
    setSuccess(null);
    const formData = new FormData(event.currentTarget);
    try {
      await submitRating.mutateAsync({
        care_request_id: Number(formData.get("care_request_id")),
        rating: Number(formData.get("rating")),
        comment: formText(formData, "comment"),
      });
      event.currentTarget.reset();
      setSuccess("Rating submitted.");
    } catch (requestError) {
      setFormError(getUserErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Ratings" description="Review completed visit ratings and feedback." />
      {user?.role === "PATIENT" ? (
        <Card>
          <CardHeader>
            <CardTitle>Submit Rating</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="grid gap-4 md:grid-cols-[minmax(0,1fr)_160px]" onSubmit={(event) => void submit(event)}>
              <div className="space-y-2">
                <Label htmlFor="care_request_id">Completed request</Label>
                <select id="care_request_id" name="care_request_id" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" required>
                  <option value="">Select request</option>
                  {completedRequests.map((request) => (
                    <option key={request.id} value={request.id}>#{request.id} {request.service_type}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="rating">Stars</Label>
                <select id="rating" name="rating" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" defaultValue="5">
                  <option value="5">5</option>
                  <option value="4">4</option>
                  <option value="3">3</option>
                  <option value="2">2</option>
                  <option value="1">1</option>
                </select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="comment">Comment</Label>
                <textarea id="comment" name="comment" className="min-h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              </div>
              {success ? <p className="text-sm text-emerald-700 md:col-span-2">{success}</p> : null}
              {formError ? <p className="text-sm text-destructive md:col-span-2">{formError}</p> : null}
              <Button className="md:col-span-2" type="submit" disabled={submitRating.isPending || completedRequests.length === 0}>
                <Star className="h-4 w-4" aria-hidden="true" />
                Submit Rating
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : null}
      {isLoading ? <LoadingState /> : null}
      {error ? (
        <ErrorState message="Ratings could not be loaded." onRetry={() => void refetch()} />
      ) : null}
      {data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.map((rating) => (
            <RatingCard key={rating.id} rating={rating} />
          ))}
        </div>
      ) : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState
          title="No Ratings"
          message="Ratings will appear after completed home-care visits."
          action={
            <Button asChild variant="outline">
              <Link to="/visits">View Completed Visits</Link>
            </Button>
          }
        />
      ) : null}
    </div>
  );
}
