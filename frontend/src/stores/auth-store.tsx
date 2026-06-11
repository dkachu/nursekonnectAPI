import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { setUnauthorizedHandler } from "@/api/client";
import { authService } from "@/services/auth.service";
import { AuthStoreContext, type AuthStoreValue } from "@/stores/auth-store-context";
import type { AuthUser, LoginResponse, PermissionSet, UserRole } from "@/types";

function getPermissions(role: UserRole | null): PermissionSet {
  return {
    role,
    canViewMedicalData: role === "PATIENT" || role === "NURSE" || role === "ADMIN",
    canManageRequests: role === "PATIENT" || role === "NURSE" || role === "ADMIN",
    canVerifyNurses: role === "ADMIN",
  };
}

export function AuthStoreProvider({ children }: { children: ReactNode }): ReactNode {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [isRestoringSession, setIsRestoringSession] = useState(true);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setCurrentUser(null);
    });

    async function restoreSession(): Promise<void> {
      try {
        const user = await authService.restoreSession();
        setCurrentUser(user);
      } catch {
        setCurrentUser(null);
      } finally {
        setIsRestoringSession(false);
      }
    }

    void restoreSession();

    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<void> => {
    const response: LoginResponse = await authService.login({ email, password });
    setCurrentUser(response.user);
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    await authService.logout();
    setCurrentUser(null);
  }, []);

  const refreshSession = useCallback(async (): Promise<void> => {
    await authService.refreshSession();
    const user = await authService.getCurrentUser();
    setCurrentUser(user);
  }, []);

  const role = currentUser?.role ?? null;
  const value = useMemo<AuthStoreValue>(
    () => ({
      currentUser,
      role,
      isAuthenticated: Boolean(currentUser),
      isRestoringSession,
      permissions: getPermissions(role),
      login,
      logout,
      refreshSession,
    }),
    [currentUser, isRestoringSession, login, logout, refreshSession, role],
  );

  return <AuthStoreContext.Provider value={value}>{children}</AuthStoreContext.Provider>;
}
