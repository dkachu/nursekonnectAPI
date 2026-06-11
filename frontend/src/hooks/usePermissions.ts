import { useAuthStore } from "@/stores/use-auth-store";
import type { PermissionSet } from "@/types";

export function usePermissions(): PermissionSet {
  return useAuthStore().permissions;
}
