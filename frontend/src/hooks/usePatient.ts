import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { patientService } from "@/services/patient.service";
import type {
  Dependent,
  DependentPayload,
  EmergencyContact,
  EmergencyContactPayload,
  PatientProfile,
  PatientProfilePatch,
} from "@/types";

export function usePatientProfile(enabled = true) {
  return useQuery({
    queryKey: ["patient-profile"],
    queryFn: () => patientService.getPatientProfile(),
    enabled,
  });
}

export function useUpdatePatientProfile() {
  const queryClient = useQueryClient();
  return useMutation<PatientProfile, Error, PatientProfilePatch>({
    mutationFn: (payload) => patientService.updatePatientProfile(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["patient-profile"] }),
  });
}

export function useEmergencyContacts() {
  return useQuery({
    queryKey: ["emergency-contacts"],
    queryFn: () => patientService.getEmergencyContacts(),
  });
}

export function useCreateEmergencyContact() {
  const queryClient = useQueryClient();
  return useMutation<EmergencyContact, Error, EmergencyContactPayload>({
    mutationFn: (payload) => patientService.createEmergencyContact(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["emergency-contacts"] }),
  });
}

export function useUpdateEmergencyContact() {
  const queryClient = useQueryClient();
  return useMutation<
    EmergencyContact,
    Error,
    { contactId: number; payload: Partial<EmergencyContactPayload> }
  >({
    mutationFn: ({ contactId, payload }) =>
      patientService.updateEmergencyContact(contactId, payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["emergency-contacts"] }),
  });
}

export function useDeleteEmergencyContact() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (contactId) => patientService.deleteEmergencyContact(contactId),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["emergency-contacts"] }),
  });
}

export function useDependents() {
  return useQuery({ queryKey: ["dependents"], queryFn: () => patientService.getDependents() });
}

export function useCreateDependent() {
  const queryClient = useQueryClient();
  return useMutation<Dependent, Error, DependentPayload>({
    mutationFn: (payload) => patientService.createDependent(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["dependents"] }),
  });
}

export function useUpdateDependent() {
  const queryClient = useQueryClient();
  return useMutation<Dependent, Error, { dependentId: number; payload: Partial<DependentPayload> }>(
    {
      mutationFn: ({ dependentId, payload }) =>
        patientService.updateDependent(dependentId, payload),
      onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["dependents"] }),
    },
  );
}

export function useDeleteDependent() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (dependentId) => patientService.deleteDependent(dependentId),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["dependents"] }),
  });
}

export function useMedicalInformation(patientId: number | null) {
  return useQuery({
    queryKey: ["medical-information", patientId],
    queryFn: () => patientService.getMedicalInformation(Number(patientId)),
    enabled: patientId !== null,
    staleTime: 0,
  });
}

export function useUpdateMedicalInformation() {
  throw new Error("Medical information updates are not exposed by the backend OpenAPI schema.");
}
