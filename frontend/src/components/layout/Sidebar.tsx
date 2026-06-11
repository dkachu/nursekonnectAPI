import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/auth/useAuth";
import { Logo } from "@/components/brand/Logo";
import { getNavigationForRole } from "@/components/layout/navigation";
import { Badge } from "@/components/ui/badge";
import { useNotificationStore } from "@/stores/use-notification-store";

export function Sidebar(): ReactNode {
  const { user } = useAuth();
  const { unreadCount } = useNotificationStore();
  const items = getNavigationForRole(user?.role);

  return (
    <aside className="hidden w-64 shrink-0 border-r border-border bg-background lg:block">
      <div className="sticky top-0 flex h-screen flex-col">
        <div className="border-b border-border px-5 py-4">
          <Logo compact />
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4" aria-label="Sidebar navigation">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${
                    isActive ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted"
                  }`
                }
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                <span className="flex-1">{item.label}</span>
                {item.href === "/notifications" && unreadCount > 0 ? (
                  <Badge variant="default">{unreadCount}</Badge>
                ) : null}
              </NavLink>
            );
          })}
        </nav>
        {user ? (
          <div className="border-t border-border p-4">
            <p className="truncate text-sm font-medium">{user.email}</p>
            <p className="text-xs text-muted-foreground">{user.role}</p>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
