import { apiClient } from "@/api/client";
import type { CareRequest, CareRequestPayload } from "@/types";

type CareRequestCreateBody = Omit<CareRequestPayload, "location">;

export const requestApi = {
  async listRequests(): Promise<CareRequest[]> {
    const response = await apiClient.get<CareRequest[]>("/api/requests/");
    return response.data;
  },
  async createRequest(payload: CareRequestCreateBody): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>("/api/requests/", payload);
    return response.data;
  },
  async getRequest(requestId: number): Promise<CareRequest> {
    const response = await apiClient.get<CareRequest>(`/api/requests/${requestId}/`);
    return response.data;
  },
  async acceptRequest(requestId: number): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>(`/api/requests/${requestId}/accept/`);
    return response.data;
  },
  async startJourney(requestId: number): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>(`/api/requests/${requestId}/start-journey/`);
    return response.data;
  },
  async markArrived(requestId: number): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>(`/api/requests/${requestId}/arrived/`);
    return response.data;
  },
  async startVisit(requestId: number): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>(`/api/requests/${requestId}/start-visit/`);
    return response.data;
  },
  async completeRequest(requestId: number): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>(`/api/requests/${requestId}/complete/`);
    return response.data;
  },
  async cancelRequest(requestId: number): Promise<CareRequest> {
    const response = await apiClient.post<CareRequest>(`/api/requests/${requestId}/cancel/`);
    return response.data;
  },
};
