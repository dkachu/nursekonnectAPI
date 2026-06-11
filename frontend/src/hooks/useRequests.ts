import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { requestService } from "@/services/request.service";
import type { CareRequest, CareRequestPayload } from "@/types";

export function useRequests() {
  return useQuery({ queryKey: ["requests"], queryFn: () => requestService.getRequests() });
}

export function useRequest(requestId: number | null) {
  return useQuery({
    queryKey: ["requests", requestId],
    queryFn: () => requestService.getRequest(Number(requestId)),
    enabled: requestId !== null,
  });
}

export function useCreateRequest() {
  const queryClient = useQueryClient();
  return useMutation<CareRequest, Error, CareRequestPayload>({
    mutationFn: (payload) => requestService.createRequest(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["requests"] }),
  });
}

function useRequestAction(action: (requestId: number) => Promise<CareRequest>) {
  const queryClient = useQueryClient();
  return useMutation<CareRequest, Error, number>({
    mutationFn: action,
    onSuccess: (request) => {
      void queryClient.invalidateQueries({ queryKey: ["requests"] });
      void queryClient.invalidateQueries({ queryKey: ["requests", request.id] });
    },
  });
}

export function useAcceptRequest() {
  return useRequestAction((requestId) => requestService.acceptRequest(requestId));
}

export function useStartJourney() {
  return useRequestAction((requestId) => requestService.startJourney(requestId));
}

export function useMarkArrived() {
  return useRequestAction((requestId) => requestService.markArrived(requestId));
}

export function useStartVisit() {
  return useRequestAction((requestId) => requestService.startVisit(requestId));
}

export function useCompleteRequest() {
  return useRequestAction((requestId) => requestService.completeRequest(requestId));
}

export function useCancelRequest() {
  return useRequestAction((requestId) => requestService.cancelRequest(requestId));
}
