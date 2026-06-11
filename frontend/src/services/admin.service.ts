import { adminApi } from "@/api/admin.api";
import type {
  AdminNurseVerificationPayload,
  CredentialReviewPayload,
  NurseCredential,
  NurseProfile,
} from "@/types";

export class AdminService {
  listNurses(): Promise<NurseProfile[]> {
    return adminApi.listNurses();
  }

  listNurseCredentials(nurseId: number): Promise<NurseCredential[]> {
    return adminApi.listNurseCredentials(nurseId);
  }

  verifyNurse(nurseId: number, payload: AdminNurseVerificationPayload): Promise<NurseProfile> {
    return adminApi.verifyNurse(nurseId, payload);
  }

  reviewCredential(
    nurseId: number,
    credentialId: number,
    payload: CredentialReviewPayload,
  ): Promise<NurseCredential> {
    return adminApi.reviewCredential(nurseId, credentialId, payload);
  }

  recalculateReputation(nurseId: number): Promise<NurseProfile> {
    return adminApi.recalculateReputation(nurseId);
  }
}

export const adminService = new AdminService();
