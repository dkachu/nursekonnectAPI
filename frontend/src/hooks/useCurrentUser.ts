import { useAuthStore } from "@/stores/use-auth-store";
import type { AuthUser } from "@/types";

export function useCurrentUser(): AuthUser | null {
  return useAuthStore().currentUser;
}
