import { patientApi } from "@/api/patient.api";
import type {
  Dependent,
  DependentPayload,
  EmergencyContact,
  EmergencyContactPayload,
  MedicalInformation,
  PatientProfile,
  PatientProfilePatch,
} from "@/types";

export class PatientService {
  getPatientProfile(): Promise<PatientProfile> {
    return patientApi.getProfile();
  }

  updatePatientProfile(payload: PatientProfilePatch): Promise<PatientProfile> {
    return patientApi.updateProfile(payload);
  }

  getEmergencyContacts(): Promise<EmergencyContact[]> {
    return patientApi.listEmergencyContacts();
  }

  createEmergencyContact(payload: EmergencyContactPayload): Promise<EmergencyContact> {
    return patientApi.createEmergencyContact(payload);
  }

  updateEmergencyContact(
    contactId: number,
    payload: Partial<EmergencyContactPayload>,
  ): Promise<EmergencyContact> {
    return patientApi.updateEmergencyContact(contactId, payload);
  }

  deleteEmergencyContact(contactId: number): Promise<void> {
    return patientApi.deleteEmergencyContact(contactId);
  }

  getDependents(): Promise<Dependent[]> {
    return patientApi.listDependents();
  }

  createDependent(payload: DependentPayload): Promise<Dependent> {
    return patientApi.createDependent(payload);
  }

  updateDependent(dependentId: number, payload: Partial<DependentPayload>): Promise<Dependent> {
    return patientApi.updateDependent(dependentId, payload);
  }

  deleteDependent(dependentId: number): Promise<void> {
    return patientApi.deleteDependent(dependentId);
  }

  getMedicalInformation(patientId: number): Promise<MedicalInformation> {
    return patientApi.getMedicalInformation(patientId);
  }
}

export const patientService = new PatientService();
