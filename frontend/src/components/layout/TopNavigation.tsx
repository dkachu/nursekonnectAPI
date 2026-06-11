import { Link, NavLink } from "react-router-dom";
import { LogOut } from "lucide-react";
import { useState, type ReactNode } from "react";
import { getApiErrorMessage } from "@/api/client";
import { useAuth } from "@/auth/useAuth";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { getNavigationForRole } from "@/components/layout/navigation";
import { Badge } from "@/components/ui/badge";
import { useNotificationStore } from "@/stores/use-notification-store";

export function TopNavigation(): ReactNode {
  const { isAuthenticated, logout, user } = useAuth();
  const { unreadCount } = useNotificationStore();
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const visibleItems = getNavigationForRole(user?.role).slice(0, 4);

  async function onLogout(): Promise<void> {
    setLogoutError(null);
    try {
      await logout();
    } catch (error) {
      setLogoutError(getApiErrorMessage(error));
    }
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to={isAuthenticated ? "/dashboard" : "/"} aria-label="NurseKonnect home">
          <Logo compact />
        </Link>
        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary navigation">
          {isAuthenticated ? (
            visibleItems.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  `rounded-md px-3 py-2 text-sm font-medium ${
                    isActive ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted"
                  }`
                }
              >
                <span>{item.label}</span>
                {item.href === "/notifications" && unreadCount > 0 ? (
                  <Badge variant="default">{unreadCount}</Badge>
                ) : null}
              </NavLink>
            ))
          ) : (
            <>
              <NavLink
                to="/"
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"
              >
                Home
              </NavLink>
              <NavLink
                to="/nurses"
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"
              >
                Find Nurses
              </NavLink>
            </>
          )}
        </nav>
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <>
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium">{user.email}</p>
                <p className="text-xs text-muted-foreground">{user.role}</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => void onLogout()}>
                <LogOut className="h-4 w-4" aria-hidden="true" />
                Logout
              </Button>
            </>
          ) : (
            <Button asChild size="sm">
              <Link to="/login">Login</Link>
            </Button>
          )}
        </div>
      </div>
      {logoutError ? (
        <div className="border-t border-border px-4 py-2 text-center text-sm text-destructive">
          {logoutError}
        </div>
      ) : null}
    </header>
  );
}
