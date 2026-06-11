import { useAuthStore } from "@/stores/use-auth-store";
import type { AuthUser } from "@/types";

export function useAuth(): {
  user: AuthUser | null;
  currentUser: AuthUser | null;
  isAuthenticated: boolean;
  isRestoringSession: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
} {
  const store = useAuthStore();
  return {
    user: store.currentUser,
    currentUser: store.currentUser,
    isAuthenticated: store.isAuthenticated,
    isRestoringSession: store.isRestoringSession,
    login: store.login,
    logout: store.logout,
    refreshSession: store.refreshSession,
  };
}
