import { nurseApi, type NearbyNurseParams } from "@/api/nurse.api";
import { trackingApi } from "@/api/tracking.api";
import type {
  AvailabilitySlot,
  LocationPayload,
  NearbyNurse,
  NurseCredential,
  NurseProfile,
  NurseStatus,
  Specialization,
} from "@/types";

export class NurseService {
  getNearbyNurses(params?: NearbyNurseParams): Promise<NearbyNurse[]> {
    return nurseApi.getNearbyNurses(params);
  }

  getNurseProfile(): Promise<NurseProfile> {
    return nurseApi.getProfile();
  }

  updateNurseProfile(payload: Partial<NurseProfile>): Promise<NurseProfile> {
    return nurseApi.updateProfile(payload);
  }

  updateLocation(payload: LocationPayload): Promise<{ location_stale?: boolean }> {
    return trackingApi.updateLocation(payload);
  }

  changeAvailability(payload: {
    status: NurseStatus;
    location_visible?: boolean;
    is_available?: boolean;
  }): Promise<NurseProfile> {
    return nurseApi.updateStatus(payload);
  }

  getNckLicenseStatusUrl(): Promise<{ url?: string }> {
    return nurseApi.getNckLicenseStatusUrl();
  }

  getSpecializations(): Promise<Specialization[]> {
    return nurseApi.listSpecializations();
  }

  replaceProfileSpecializations(specializations: string[]): Promise<NurseProfile> {
    return nurseApi.replaceProfileSpecializations({ specializations });
  }

  getCredentials(): Promise<NurseCredential[]> {
    return nurseApi.listCredentials();
  }

  uploadCredential(payload: FormData): Promise<NurseCredential> {
    return nurseApi.uploadCredential(payload);
  }

  getAvailability(): Promise<AvailabilitySlot[]> {
    return nurseApi.listAvailability();
  }

  createAvailability(payload: Omit<AvailabilitySlot, "id">): Promise<AvailabilitySlot> {
    return nurseApi.createAvailability(payload);
  }

  updateAvailability(
    slotId: number,
    payload: Partial<Omit<AvailabilitySlot, "id">>,
  ): Promise<AvailabilitySlot> {
    return nurseApi.updateAvailability(slotId, payload);
  }

  deleteAvailability(slotId: number): Promise<void> {
    return nurseApi.deleteAvailability(slotId);
  }
}

export const nurseService = new NurseService();
