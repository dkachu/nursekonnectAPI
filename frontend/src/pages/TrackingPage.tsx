import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { LocateFixed, Radio } from "lucide-react";
import { useAuth } from "@/auth/useAuth";
import { JourneyMap } from "@/components/maps/JourneyMap";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrackingStatusCard } from "@/features/tracking/components/TrackingStatusCard";
import { useGeolocation } from "@/hooks/useGeolocation";
import {
  useRequestTrackingLocations,
  useSubmitTrackingLocation,
  useUpdateLocation,
} from "@/hooks/useLocation";
import { useRequests } from "@/hooks/useRequests";
import type { Coordinates } from "@/types";
import { getUserErrorMessage } from "@/utils/errors";

const trackableStatuses = new Set(["ACCEPTED", "PREPARING", "NURSE_EN_ROUTE", "ARRIVED", "IN_PROGRESS"]);

export function TrackingPage(): ReactNode {
  const geolocation = useGeolocation();
  const updateLocation = useUpdateLocation();
  const submitTracking = useSubmitTrackingLocation();
  const requests = useRequests();
  const { user } = useAuth();
  const activeRequests = useMemo(
    () => (requests.data ?? []).filter((request) => trackableStatuses.has(request.status)),
    [requests.data],
  );
  const [selectedRequestId, setSelectedRequestId] = useState<number | null>(null);
  const requestId = selectedRequestId ?? activeRequests[0]?.id ?? null;
  const trackingLocations = useRequestTrackingLocations(requestId, user?.role !== "NURSE");
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const latestTracking = trackingLocations.data?.[0];
  const nurseLocation =
    latestTracking?.latitude && latestTracking.longitude
      ? { latitude: latestTracking.latitude, longitude: latestTracking.longitude }
      : user?.role === "NURSE"
        ? coordinates
        : null;

  async function submitLocation(): Promise<void> {
    setSuccess(null);
    setError(null);
    try {
      const nextCoordinates = await geolocation.requestLocation();
      if (user?.role === "NURSE") {
        await submitTracking.mutateAsync(nextCoordinates);
        setSuccess("Journey tracking point submitted.");
      } else {
        await updateLocation.mutateAsync(nextCoordinates);
        setSuccess("Current location submitted.");
      }
      setCoordinates(nextCoordinates);
    } catch (requestError) {
      setError(getUserErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Journey Tracking"
        description="Follow active nurse journeys and submit GPS updates from care devices."
        actions={
          <Button
            onClick={() => void submitLocation()}
            disabled={geolocation.loading || updateLocation.isPending || submitTracking.isPending}
          >
            <LocateFixed className="h-4 w-4" aria-hidden="true" />
            {geolocation.loading || updateLocation.isPending || submitTracking.isPending
              ? "Submitting"
              : user?.role === "NURSE"
                ? "Submit Journey GPS"
                : "Submit Current GPS"}
          </Button>
        }
      />
      {requests.isLoading ? <LoadingState /> : null}
      {success ? <p className="text-sm text-emerald-700">{success}</p> : null}
      {error ? <ErrorState message={error} /> : null}
      {requests.error ? <ErrorState message="Requests could not be loaded for tracking." /> : null}
      {activeRequests.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Active Journey</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-[minmax(0,280px)_minmax(0,1fr)]">
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              value={requestId ?? ""}
              onChange={(event) => setSelectedRequestId(Number(event.target.value))}
            >
              {activeRequests.map((request) => (
                <option key={request.id} value={request.id}>
                  #{request.id} {request.service_type} | {request.status}
                </option>
              ))}
            </select>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Radio className="h-4 w-4 text-primary" aria-hidden="true" />
              {trackingLocations.isFetching ? "Refreshing tracking points" : "Tracking refreshes every 30 seconds"}
            </div>
          </CardContent>
        </Card>
      ) : null}
      <JourneyMap
        patientLocation={user?.role === "PATIENT" ? coordinates : null}
        nurseLocation={nurseLocation}
        etaMinutes={null}
      />
      <TrackingStatusCard coordinates={nurseLocation ?? coordinates} />
      {trackingLocations.data?.length ? (
        <Card>
          <CardHeader>
            <CardTitle>Recent GPS Points</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {trackingLocations.data.slice(0, 5).map((location) => (
              <div key={location.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
                <span>{location.latitude?.toFixed(6)}, {location.longitude?.toFixed(6)}</span>
                <span className="text-muted-foreground">{new Date(location.recorded_at).toLocaleString()}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}
      {!requests.isLoading && activeRequests.length === 0 ? (
        <EmptyState
          title="No Active Journey"
          message="Live journey tracking starts after a nurse accepts and begins travel."
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
