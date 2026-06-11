import { trackingApi } from "@/api/tracking.api";
import type { LocationPayload, TrackingLocation, TrackingLocationPayload } from "@/types";

export class TrackingService {
  updateLocation(payload: LocationPayload): Promise<{ location_stale?: boolean }> {
    return trackingApi.updateLocation(payload);
  }

  submitTrackingLocation(payload: TrackingLocationPayload): Promise<TrackingLocation> {
    return trackingApi.submitTrackingLocation(payload);
  }

  listRequestLocations(requestId: number): Promise<TrackingLocation[]> {
    return trackingApi.listRequestLocations(requestId);
  }
}

export const trackingService = new TrackingService();
