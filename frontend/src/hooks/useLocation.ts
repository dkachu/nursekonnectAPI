import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { trackingService } from "@/services/tracking.service";
import type { LocationPayload, TrackingLocation, TrackingLocationPayload } from "@/types";

export function useUpdateLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LocationPayload) => trackingService.updateLocation(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["nearby-nurses"] });
    },
  });
}

export function useSubmitTrackingLocation() {
  const queryClient = useQueryClient();
  return useMutation<TrackingLocation, Error, TrackingLocationPayload>({
    mutationFn: (payload) => trackingService.submitTrackingLocation(payload),
    onSuccess: (location) => {
      if (location.care_request_id) {
        void queryClient.invalidateQueries({
          queryKey: ["tracking-locations", location.care_request_id],
        });
      }
    },
  });
}

export function useRequestTrackingLocations(requestId: number | null, enabled = true) {
  return useQuery({
    queryKey: ["tracking-locations", requestId],
    queryFn: () => trackingService.listRequestLocations(Number(requestId)),
    enabled: enabled && requestId !== null,
    refetchInterval: 30000,
  });
}
