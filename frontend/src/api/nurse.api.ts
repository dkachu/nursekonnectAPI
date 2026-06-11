import { apiClient } from "@/api/client";
import type {
  AvailabilitySlot,
  NearbyNurse,
  NurseCredential,
  NurseProfile,
  NurseStatus,
  Specialization,
} from "@/types";

export interface NearbyNurseParams {
  specialization?: string;
  limit?: number;
}

export const nurseApi = {
  async getProfile(): Promise<NurseProfile> {
    const response = await apiClient.get<NurseProfile>("/api/nurse/profile/");
    return response.data;
  },
  async updateProfile(payload: Partial<NurseProfile>): Promise<NurseProfile> {
    const response = await apiClient.patch<NurseProfile>("/api/nurse/profile/", payload);
    return response.data;
  },
  async getNearbyNurses(params?: NearbyNurseParams): Promise<NearbyNurse[]> {
    const response = await apiClient.get<NearbyNurse[]>("/api/nurses/nearby/", { params });
    return response.data;
  },
  getNckLicenseStatusUrl(): Promise<{ url?: string }> {
    return Promise.resolve({
      url: `${apiClient.defaults.baseURL ?? ""}/api/nurses/nck-license-status/`,
    });
  },
  async listSpecializations(): Promise<Specialization[]> {
    const response = await apiClient.get<Specialization[]>("/api/nurse/specializations/");
    return response.data;
  },
  async replaceProfileSpecializations(payload: {
    specializations: string[];
  }): Promise<NurseProfile> {
    const response = await apiClient.put<NurseProfile>(
      "/api/nurse/profile/specializations/",
      payload,
    );
    return response.data;
  },
  async listCredentials(): Promise<NurseCredential[]> {
    const response = await apiClient.get<NurseCredential[]>("/api/nurse/credentials/");
    return response.data;
  },
  async uploadCredential(payload: FormData): Promise<NurseCredential> {
    const response = await apiClient.post<NurseCredential>("/api/nurse/credentials/", payload, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },
  async listAvailability(): Promise<AvailabilitySlot[]> {
    const response = await apiClient.get<AvailabilitySlot[]>("/api/nurse/availability/");
    return response.data;
  },
  async createAvailability(payload: Omit<AvailabilitySlot, "id">): Promise<AvailabilitySlot> {
    const response = await apiClient.post<AvailabilitySlot>("/api/nurse/availability/", payload);
    return response.data;
  },
  async updateAvailability(
    slotId: number,
    payload: Partial<Omit<AvailabilitySlot, "id">>,
  ): Promise<AvailabilitySlot> {
    const response = await apiClient.patch<AvailabilitySlot>(
      `/api/nurse/availability/${slotId}/`,
      payload,
    );
    return response.data;
  },
  async deleteAvailability(slotId: number): Promise<void> {
    await apiClient.delete(`/api/nurse/availability/${slotId}/`);
  },
  async updateStatus(payload: {
    status: NurseStatus;
    location_visible?: boolean;
    is_available?: boolean;
  }): Promise<NurseProfile> {
    const response = await apiClient.post<NurseProfile>("/api/nurse/status/", payload);
    return response.data;
  },
};
