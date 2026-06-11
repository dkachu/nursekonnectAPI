import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { NearbyNurseParams } from "@/api/nurse.api";
import { nurseService } from "@/services/nurse.service";
import type { AvailabilitySlot, NurseCredential, NurseProfile, NurseStatus } from "@/types";

export function useNearbyNurses(params?: NearbyNurseParams, enabled = false) {
  return useQuery({
    queryKey: ["nearby-nurses", params],
    queryFn: () => nurseService.getNearbyNurses(params),
    enabled,
  });
}

export function useNurseProfile() {
  return useQuery({ queryKey: ["nurse-profile"], queryFn: () => nurseService.getNurseProfile() });
}

export function useUpdateNurseProfile() {
  const queryClient = useQueryClient();
  return useMutation<NurseProfile, Error, Partial<NurseProfile>>({
    mutationFn: (payload) => nurseService.updateNurseProfile(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["nurse-profile"] }),
  });
}

export function useNckLicenseStatusUrl() {
  return useQuery({
    queryKey: ["nck-license-status"],
    queryFn: () => nurseService.getNckLicenseStatusUrl(),
  });
}

export function useSpecializations() {
  return useQuery({
    queryKey: ["specializations"],
    queryFn: () => nurseService.getSpecializations(),
  });
}

export function useProfileSpecializations() {
  return useQuery({
    queryKey: ["profile-specializations"],
    queryFn: () => nurseService.getNurseProfile(),
  });
}

export function useReplaceProfileSpecializations() {
  const queryClient = useQueryClient();
  return useMutation<NurseProfile, Error, string[]>({
    mutationFn: (specializations) => nurseService.replaceProfileSpecializations(specializations),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["profile-specializations"] });
      void queryClient.invalidateQueries({ queryKey: ["nurse-profile"] });
    },
  });
}

export function useCredentials() {
  return useQuery({ queryKey: ["credentials"], queryFn: () => nurseService.getCredentials() });
}

export function useUploadCredential() {
  const queryClient = useQueryClient();
  return useMutation<NurseCredential, Error, FormData>({
    mutationFn: (payload) => nurseService.uploadCredential(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["credentials"] }),
  });
}

export function useAvailability() {
  return useQuery({ queryKey: ["availability"], queryFn: () => nurseService.getAvailability() });
}

export function useCreateAvailability() {
  const queryClient = useQueryClient();
  return useMutation<AvailabilitySlot, Error, Omit<AvailabilitySlot, "id">>({
    mutationFn: (payload) => nurseService.createAvailability(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["availability"] }),
  });
}

export function useUpdateAvailability() {
  const queryClient = useQueryClient();
  return useMutation<
    AvailabilitySlot,
    Error,
    { slotId: number; payload: Partial<Omit<AvailabilitySlot, "id">> }
  >({
    mutationFn: ({ slotId, payload }) => nurseService.updateAvailability(slotId, payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["availability"] }),
  });
}

export function useDeleteAvailability() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (slotId) => nurseService.deleteAvailability(slotId),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["availability"] }),
  });
}

export function useChangeAvailability() {
  const queryClient = useQueryClient();
  return useMutation<
    NurseProfile,
    Error,
    { status: NurseStatus; location_visible?: boolean; is_available?: boolean }
  >({
    mutationFn: (payload) => nurseService.changeAvailability(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["nurse-profile"] }),
  });
}
