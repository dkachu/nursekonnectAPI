import type { ReactNode } from "react";
import { useState } from "react";
import { Bell, ClipboardList, Stethoscope, Star } from "lucide-react";
import { useAuth } from "@/auth/useAuth";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { useNearbyNurses } from "@/hooks/useNurses";
import { useNotifications } from "@/hooks/useNotifications";
import { useRatings } from "@/hooks/useRatings";
import { useRequests } from "@/hooks/useRequests";
import { useVisitNotes } from "@/hooks/useVisits";
import {
  useAdminNurseCredentials,
  useAdminNurses,
  useRecalculateReputation,
  useReviewCredential,
  useVerifyNurse,
} from "@/hooks/useAdmin";
import type { NurseProfile, VerificationStatus } from "@/types";

export function DashboardPage(): ReactNode {
  const { user } = useAuth();
  const requests = useRequests();
  const visits = useVisitNotes();
  const ratings = useRatings();
  const notifications = useNotifications();
  const nearbyNurses = useNearbyNurses(undefined, user?.role === "PATIENT");
  const adminNurses = useAdminNurses(user?.role === "ADMIN");
  const [selectedNurseId, setSelectedNurseId] = useState<number | null>(null);
  const adminCredentials = useAdminNurseCredentials(
    user?.role === "ADMIN" ? selectedNurseId : null,
  );
  const verifyNurse = useVerifyNurse();
  const reviewCredential = useReviewCredential();
  const recalculateReputation = useRecalculateReputation();

  const activeRequests =
    requests.data?.filter(
      (request) => !["COMPLETED", "CANCELLED", "EXPIRED"].includes(request.status),
    ).length ?? 0;
  const completedVisits = visits.data?.length ?? 0;
  const nurseCount = nearbyNurses.data?.length ?? 0;
  const notificationCount = notifications.unreadCount;
  const isLoading =
    requests.isLoading || visits.isLoading || ratings.isLoading || notifications.isLoading;
  const error =
    requests.error ?? visits.error ?? ratings.error ?? notifications.error ?? nearbyNurses.error;
  const summaries = [
    { label: "Active Requests", value: activeRequests, icon: ClipboardList },
    {
      label: user?.role === "PATIENT" ? "Nearby Nurses" : "Completed Visits",
      value: user?.role === "PATIENT" ? nurseCount : completedVisits,
      icon: Stethoscope,
    },
    { label: "Notifications", value: notificationCount, icon: Bell },
    { label: "Ratings", value: ratings.data?.length ?? 0, icon: Star },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Monitor requests, visits, notifications, and account readiness from one quiet workspace."
        actions={user ? <Badge variant="neutral">{user.role}</Badge> : null}
      />
      {isLoading ? <LoadingState /> : null}
      {error ? (
        <ErrorState
          message="Dashboard data could not be loaded. Check your session and backend connection."
          onRetry={() => {
            void requests.refetch();
            void visits.refetch();
            void ratings.refetch();
            void notifications.refetch();
            void nearbyNurses.refetch();
          }}
        />
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {summaries.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {item.label}
                </CardTitle>
                <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-semibold">{item.value}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>
      {user?.role === "ADMIN" ? (
        <AdminVerificationWorkflow
          credentials={adminCredentials.data ?? []}
          nurses={adminNurses.data ?? []}
          onRecalculate={(nurseId) => void recalculateReputation.mutateAsync(nurseId)}
          onReview={(nurseId, credentialId, status) =>
            void reviewCredential.mutateAsync({
              nurseId,
              credentialId,
              payload: { verification_status: status, review_notes: "Reviewed from dashboard." },
            })
          }
          onSelectNurse={setSelectedNurseId}
          onVerify={(nurseId, status) =>
            void verifyNurse.mutateAsync({
              nurseId,
              payload: { nck_verification_status: status },
            })
          }
          selectedNurseId={selectedNurseId}
        />
      ) : null}
    </div>
  );
}

function AdminVerificationWorkflow({
  credentials,
  nurses,
  onRecalculate,
  onReview,
  onSelectNurse,
  onVerify,
  selectedNurseId,
}: {
  credentials: Array<{ id: number; credential_type: string; verification_status: VerificationStatus }>;
  nurses: NurseProfile[];
  onRecalculate: (nurseId: number) => void;
  onReview: (nurseId: number, credentialId: number, status: VerificationStatus) => void;
  onSelectNurse: (nurseId: number) => void;
  onVerify: (nurseId: number, status: VerificationStatus) => void;
  selectedNurseId: number | null;
}): ReactNode {
  const selectedNurse = nurses.find((nurse) => nurse.id === selectedNurseId) ?? nurses[0];
  const activeNurseId = selectedNurse?.id ?? null;

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(320px,0.8fr)]">
      <Card>
        <CardHeader>
          <CardTitle>Nurse Verification</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {nurses.map((nurse) => (
            <div
              key={nurse.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-border px-3 py-3"
            >
              <button
                className="text-left"
                type="button"
                onClick={() => onSelectNurse(nurse.id)}
              >
                <p className="text-sm font-medium">
                  {nurse.first_name} {nurse.last_name}
                </p>
                <p className="text-xs text-muted-foreground">{nurse.email}</p>
              </button>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="neutral">{nurse.nck_verification_status}</Badge>
                <Button size="sm" variant="secondary" onClick={() => onVerify(nurse.id, "UNDER_REVIEW")}>
                  Review
                </Button>
                <Button size="sm" onClick={() => onVerify(nurse.id, "VERIFIED")}>Verify</Button>
                <Button size="sm" variant="destructive" onClick={() => onVerify(nurse.id, "REJECTED")}>
                  Reject
                </Button>
                <Button size="sm" variant="outline" onClick={() => onRecalculate(nurse.id)}>
                  Reputation
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Credential Review</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {activeNurseId === null ? (
            <p className="text-sm text-muted-foreground">No nurse selected.</p>
          ) : null}
          {credentials.length === 0 && activeNurseId !== null ? (
            <p className="text-sm text-muted-foreground">No credentials uploaded.</p>
          ) : null}
          {credentials.map((credential) => (
            <div key={credential.id} className="rounded-md border border-border px-3 py-3">
              <div className="mb-3 flex items-center justify-between gap-3">
                <p className="text-sm font-medium">{credential.credential_type}</p>
                <Badge variant="neutral">{credential.verification_status}</Badge>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" onClick={() => activeNurseId && onReview(activeNurseId, credential.id, "VERIFIED")}>
                  Approve
                </Button>
                <Button size="sm" variant="destructive" onClick={() => activeNurseId && onReview(activeNurseId, credential.id, "REJECTED")}>
                  Reject
                </Button>
                <Button size="sm" variant="outline" onClick={() => activeNurseId && onReview(activeNurseId, credential.id, "EXPIRED")}>
                  Expired
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
