import { createContext } from "react";
import type { AuthUser, PermissionSet, UserRole } from "@/types";

export interface AuthStoreValue {
  currentUser: AuthUser | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isRestoringSession: boolean;
  permissions: PermissionSet;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export const AuthStoreContext = createContext<AuthStoreValue | null>(null);
