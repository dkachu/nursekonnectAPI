import {
  Activity,
  Bell,
  ClipboardList,
  Home,
  MapPin,
  Star,
  Stethoscope,
  UserRound,
} from "lucide-react";
import type { ComponentType, SVGProps } from "react";
import type { UserRole } from "@/types/auth";

export interface NavigationItem {
  label: string;
  href: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
  roles?: UserRole[];
}

export const navigationItems: NavigationItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: Home },
  { label: "Find Nurses", href: "/nurses", icon: Stethoscope, roles: ["PATIENT", "ADMIN"] },
  { label: "Requests", href: "/requests", icon: ClipboardList },
  { label: "Tracking", href: "/tracking", icon: MapPin },
  { label: "Visits", href: "/visits", icon: Activity },
  { label: "Ratings", href: "/ratings", icon: Star },
  { label: "Notifications", href: "/notifications", icon: Bell },
  { label: "Profile", href: "/profile", icon: UserRound },
];

export function getNavigationForRole(role?: UserRole): NavigationItem[] {
  return navigationItems.filter((item) => !item.roles || (role && item.roles.includes(role)));
}
