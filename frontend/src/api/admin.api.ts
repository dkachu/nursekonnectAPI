import { apiClient } from "@/api/client";
import type {
  AdminNurseVerificationPayload,
  CredentialReviewPayload,
  NurseCredential,
  NurseProfile,
} from "@/types";

export const adminApi = {
  async listNurses(): Promise<NurseProfile[]> {
    const response = await apiClient.get<NurseProfile[]>("/api/admin/nurses/");
    return response.data;
  },
  async listNurseCredentials(nurseId: number): Promise<NurseCredential[]> {
    const response = await apiClient.get<NurseCredential[]>(
      `/api/admin/nurses/${nurseId}/credentials/`,
    );
    return response.data;
  },
  async verifyNurse(
    nurseId: number,
    payload: AdminNurseVerificationPayload,
  ): Promise<NurseProfile> {
    const response = await apiClient.patch<NurseProfile>(
      `/api/admin/nurses/${nurseId}/verification/`,
      payload,
    );
    return response.data;
  },
  async reviewCredential(
    nurseId: number,
    credentialId: number,
    payload: CredentialReviewPayload,
  ): Promise<NurseCredential> {
    const response = await apiClient.patch<NurseCredential>(
      `/api/admin/nurses/${nurseId}/credentials/${credentialId}/review/`,
      payload,
    );
    return response.data;
  },
  async recalculateReputation(nurseId: number): Promise<NurseProfile> {
    const response = await apiClient.post<NurseProfile>(
      `/api/admin/nurses/${nurseId}/reputation/recalculate/`,
    );
    return response.data;
  },
};
