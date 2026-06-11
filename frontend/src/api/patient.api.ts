import { apiClient } from "@/api/client";
import type {
  Dependent,
  DependentPayload,
  EmergencyContact,
  EmergencyContactPayload,
  MedicalInformation,
  PatientProfile,
  PatientProfilePatch,
} from "@/types";

export const patientApi = {
  async getProfile(): Promise<PatientProfile> {
    const response = await apiClient.get<PatientProfile>("/api/patient/profile/");
    return response.data;
  },
  async updateProfile(payload: PatientProfilePatch): Promise<PatientProfile> {
    const response = await apiClient.patch<PatientProfile>("/api/patient/profile/", payload);
    return response.data;
  },
  async listEmergencyContacts(): Promise<EmergencyContact[]> {
    const response = await apiClient.get<EmergencyContact[]>("/api/patient/emergency-contacts/");
    return response.data;
  },
  async createEmergencyContact(payload: EmergencyContactPayload): Promise<EmergencyContact> {
    const response = await apiClient.post<EmergencyContact>(
      "/api/patient/emergency-contacts/",
      payload,
    );
    return response.data;
  },
  async updateEmergencyContact(
    contactId: number,
    payload: Partial<EmergencyContactPayload>,
  ): Promise<EmergencyContact> {
    const response = await apiClient.patch<EmergencyContact>(
      `/api/patient/emergency-contacts/${contactId}/`,
      payload,
    );
    return response.data;
  },
  async deleteEmergencyContact(contactId: number): Promise<void> {
    await apiClient.delete(`/api/patient/emergency-contacts/${contactId}/`);
  },
  async listDependents(): Promise<Dependent[]> {
    const response = await apiClient.get<Dependent[]>("/api/patient/dependents/");
    return response.data;
  },
  async createDependent(payload: DependentPayload): Promise<Dependent> {
    const response = await apiClient.post<Dependent>("/api/patient/dependents/", payload);
    return response.data;
  },
  async updateDependent(
    dependentId: number,
    payload: Partial<DependentPayload>,
  ): Promise<Dependent> {
    const response = await apiClient.patch<Dependent>(
      `/api/patient/dependents/${dependentId}/`,
      payload,
    );
    return response.data;
  },
  async deleteDependent(dependentId: number): Promise<void> {
    await apiClient.delete(`/api/patient/dependents/${dependentId}/`);
  },
  async getMedicalInformation(patientId: number): Promise<MedicalInformation> {
    const response = await apiClient.get<MedicalInformation>(
      `/api/patients/${patientId}/medical-information/`,
    );
    return response.data;
  },
};
