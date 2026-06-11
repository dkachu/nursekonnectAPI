import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { adminService } from "@/services/admin.service";
import type {
  AdminNurseVerificationPayload,
  CredentialReviewPayload,
  NurseCredential,
  NurseProfile,
} from "@/types";

export function useAdminNurses(enabled = true) {
  return useQuery({
    queryKey: ["admin-nurses"],
    queryFn: () => adminService.listNurses(),
    enabled,
  });
}

export function useAdminNurseCredentials(nurseId: number | null) {
  return useQuery({
    queryKey: ["admin-nurse-credentials", nurseId],
    queryFn: () => adminService.listNurseCredentials(Number(nurseId)),
    enabled: nurseId !== null,
  });
}

export function useVerifyNurse() {
  const queryClient = useQueryClient();
  return useMutation<
    NurseProfile,
    Error,
    { nurseId: number; payload: AdminNurseVerificationPayload }
  >({
    mutationFn: ({ nurseId, payload }) => adminService.verifyNurse(nurseId, payload),
    onSuccess: (_nurse, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-nurses"] });
      void queryClient.invalidateQueries({
        queryKey: ["admin-nurse-credentials", variables.nurseId],
      });
    },
  });
}

export function useReviewCredential() {
  const queryClient = useQueryClient();
  return useMutation<
    NurseCredential,
    Error,
    { nurseId: number; credentialId: number; payload: CredentialReviewPayload }
  >({
    mutationFn: ({ nurseId, credentialId, payload }) =>
      adminService.reviewCredential(nurseId, credentialId, payload),
    onSuccess: (_credential, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["credentials"] });
      void queryClient.invalidateQueries({
        queryKey: ["admin-nurse-credentials", variables.nurseId],
      });
    },
  });
}

export function useRecalculateReputation() {
  const queryClient = useQueryClient();
  return useMutation<NurseProfile, Error, number>({
    mutationFn: (nurseId) => adminService.recalculateReputation(nurseId),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["admin-nurses"] }),
  });
}
