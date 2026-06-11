import type { ReactNode } from "react";
import { useState } from "react";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { NurseCard } from "@/features/nurses/components/NurseCard";
import { useGeolocation } from "@/hooks/useGeolocation";
import { useUpdateLocation } from "@/hooks/useLocation";
import { useNearbyNurses } from "@/hooks/useNurses";
import type { Coordinates } from "@/types";
import { getUserErrorMessage } from "@/utils/errors";

export function NearbyNursesPage(): ReactNode {
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const geolocation = useGeolocation();
  const updateLocation = useUpdateLocation();
  const { data, isLoading, error, refetch } = useNearbyNurses({ limit: 50 }, coordinates !== null);

  const nurses = data ?? [];

  async function refreshFromGps(): Promise<void> {
    setActionError(null);
    setSuccess(null);
    try {
      const nextCoordinates = await geolocation.requestLocation();
      await updateLocation.mutateAsync(nextCoordinates);
      setCoordinates(nextCoordinates);
      setSuccess("Location updated. Nearby nurses are being refreshed.");
    } catch (requestError) {
      setActionError(getUserErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Find Nurses"
        description="Verified, online, available nurses within the configured care radius."
        actions={
          <Button
            onClick={() => void refreshFromGps()}
            disabled={geolocation.loading || updateLocation.isPending}
          >
            {geolocation.loading || updateLocation.isPending
              ? "Updating Location"
              : "Use Current Location"}
          </Button>
        }
      />
      {success ? <p className="text-sm text-emerald-700">{success}</p> : null}
      {actionError ? <ErrorState message={actionError} /> : null}
      {error ? (
        <ErrorState message="Nearby nurses could not be loaded." onRetry={() => void refetch()} />
      ) : null}
      {isLoading ? <LoadingState /> : null}
      {!isLoading && nurses.length === 0 ? (
        <EmptyState
          title="No Nurses Found"
          message="No verified online nurses are currently available near your GPS location."
          action={<Button onClick={() => void refreshFromGps()}>Refresh Nurses</Button>}
        />
      ) : null}
      {nurses.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {nurses.map((nurse) => (
            <NurseCard key={nurse.id} nurse={nurse} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
