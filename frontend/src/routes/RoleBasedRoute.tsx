import { Navigate, Outlet } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/auth/useAuth";
import { LoadingState } from "@/components/states/LoadingState";
import type { UserRole } from "@/types/auth";

interface RoleBasedRouteProps {
  roles: UserRole[];
}

export function RoleBasedRoute({ roles }: RoleBasedRouteProps): ReactNode {
  const { isRestoringSession, user } = useAuth();

  if (isRestoringSession) {
    return <LoadingState />;
  }

  if (!user || !roles.includes(user.role)) {
    return <Navigate to="/forbidden" replace />;
  }

  return <Outlet />;
}
