import { requestApi } from "@/api/request.api";
import { trackingApi } from "@/api/tracking.api";
import type { CareRequest, CareRequestPayload } from "@/types";

export class RequestService {
  getRequests(): Promise<CareRequest[]> {
    return requestApi.listRequests();
  }

  async createRequest(payload: CareRequestPayload): Promise<CareRequest> {
    const { location, ...requestPayload } = payload;
    await trackingApi.updateLocation(location);
    return requestApi.createRequest(requestPayload);
  }

  getRequest(requestId: number): Promise<CareRequest> {
    return requestApi.getRequest(requestId);
  }

  acceptRequest(requestId: number): Promise<CareRequest> {
    return requestApi.acceptRequest(requestId);
  }

  startJourney(requestId: number): Promise<CareRequest> {
    return requestApi.startJourney(requestId);
  }

  markArrived(requestId: number): Promise<CareRequest> {
    return requestApi.markArrived(requestId);
  }

  startVisit(requestId: number): Promise<CareRequest> {
    return requestApi.startVisit(requestId);
  }

  completeRequest(requestId: number): Promise<CareRequest> {
    return requestApi.completeRequest(requestId);
  }

  cancelRequest(requestId: number): Promise<CareRequest> {
    return requestApi.cancelRequest(requestId);
  }
}

export const requestService = new RequestService();
