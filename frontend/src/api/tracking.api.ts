import { apiClient } from "@/api/client";
import type { LocationPayload, TrackingLocation, TrackingLocationPayload } from "@/types";

export const trackingApi = {
  async updateLocation(payload: LocationPayload): Promise<{ location_stale?: boolean }> {
    const response = await apiClient.post<{ location_stale?: boolean }>(
      "/api/location/update/",
      payload,
    );
    return response.data;
  },
  async submitTrackingLocation(payload: TrackingLocationPayload): Promise<TrackingLocation> {
    const response = await apiClient.post<TrackingLocation>("/api/tracking/location/", payload);
    return response.data;
  },
  async listRequestLocations(requestId: number): Promise<TrackingLocation[]> {
    const response = await apiClient.get<TrackingLocation[]>(
      `/api/tracking/requests/${requestId}/locations/`,
    );
    return response.data;
  },
};
