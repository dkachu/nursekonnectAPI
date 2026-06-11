import type { ReactNode } from "react";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { FilePlus } from "lucide-react";
import { useAuth } from "@/auth/useAuth";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { VisitNoteCard } from "@/features/visits/components/VisitNoteCard";
import { useRequests } from "@/hooks/useRequests";
import { useCreateVisitNote, useVisitNotes } from "@/hooks/useVisits";
import { getUserErrorMessage } from "@/utils/errors";

function formText(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

export function VisitsPage(): ReactNode {
  const { user } = useAuth();
  const { data = [], isLoading, error, refetch } = useVisitNotes();
  const requests = useRequests();
  const createVisitNote = useCreateVisitNote();
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const activeVisitRequests = (requests.data ?? []).filter((request) =>
    ["ARRIVED", "IN_PROGRESS"].includes(request.status),
  );

  async function submitVisitNote(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setFormError(null);
    setSuccess(null);
    const formData = new FormData(event.currentTarget);
    try {
      await createVisitNote.mutateAsync({
        care_request_id: Number(formData.get("care_request_id")),
        vitals: formText(formData, "vitals"),
        observations: formText(formData, "observations"),
        medication_given: formText(formData, "medication_given"),
        recommendations: formText(formData, "recommendations"),
        follow_up_required: formData.get("follow_up_required") === "on",
        follow_up_schedule: formText(formData, "follow_up_schedule"),
      });
      event.currentTarget.reset();
      setSuccess("Visit note saved.");
    } catch (requestError) {
      setFormError(getUserErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Visits"
        description="Visit notes, vitals, medications, recommendations, and follow-ups."
      />
      {user?.role === "NURSE" ? (
        <Card>
          <CardHeader>
            <CardTitle>Record Visit Note</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="grid gap-4 md:grid-cols-2" onSubmit={(event) => void submitVisitNote(event)}>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="care_request_id">Care request</Label>
                <select id="care_request_id" name="care_request_id" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" required>
                  <option value="">Select active visit</option>
                  {activeVisitRequests.map((request) => (
                    <option key={request.id} value={request.id}>#{request.id} {request.service_type} | {request.status}</option>
                  ))}
                </select>
              </div>
              <VisitTextArea name="vitals" label="Vitals" />
              <VisitTextArea name="observations" label="Observations" />
              <VisitTextArea name="medication_given" label="Medication given" />
              <VisitTextArea name="recommendations" label="Recommendations" />
              <label className="flex items-center gap-2 text-sm">
                <input name="follow_up_required" type="checkbox" />
                Follow-up required
              </label>
              <div className="space-y-2">
                <Label htmlFor="follow_up_schedule">Follow-up schedule</Label>
                <select id="follow_up_schedule" name="follow_up_schedule" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm">
                  <option value="">No follow-up</option>
                  <option value="1_DAY">1 Day</option>
                  <option value="3_DAYS">3 Days</option>
                  <option value="1_WEEK">1 Week</option>
                  <option value="2_WEEKS">2 Weeks</option>
                  <option value="1_MONTH">1 Month</option>
                </select>
              </div>
              {success ? <p className="text-sm text-emerald-700 md:col-span-2">{success}</p> : null}
              {formError ? <p className="text-sm text-destructive md:col-span-2">{formError}</p> : null}
              <Button className="md:col-span-2" type="submit" disabled={createVisitNote.isPending || activeVisitRequests.length === 0}>
                <FilePlus className="h-4 w-4" aria-hidden="true" />
                Save Visit Note
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : null}
      {isLoading ? <LoadingState /> : null}
      {error ? (
        <ErrorState message="Visit notes could not be loaded." onRetry={() => void refetch()} />
      ) : null}
      {data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {data.map((note) => (
            <VisitNoteCard key={note.id} note={note} />
          ))}
        </div>
      ) : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState
          title="No Visit Notes"
          message="Visit documentation appears here after care has started."
          action={
            <Button asChild variant="outline">
              <Link to="/requests">View Requests</Link>
            </Button>
          }
        />
      ) : null}
    </div>
  );
}

function VisitTextArea({ label, name }: { label: string; name: string }): ReactNode {
  return (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <textarea id={name} name={name} className="min-h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
    </div>
  );
}
