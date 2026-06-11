import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/auth/useAuth";
import { getNavigationForRole } from "@/components/layout/navigation";

export function MobileNavigation(): ReactNode {
  const { user } = useAuth();
  const items = getNavigationForRole(user?.role).slice(0, 5);

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t border-border bg-background lg:hidden"
      aria-label="Mobile navigation"
    >
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              `flex min-h-16 flex-col items-center justify-center gap-1 px-1 text-xs font-medium ${
                isActive ? "text-primary" : "text-muted-foreground"
              }`
            }
          >
            <Icon className="h-5 w-5" aria-hidden="true" />
            <span className="max-w-full truncate">{item.label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
}
