import { lazy, Suspense, type ReactNode } from "react";
import type { RouteObject } from "react-router-dom";
import { RouteLoadingState } from "@/components/states/RouteLoadingState";
import { AppShell } from "@/layouts/AppShell";
import { PublicLayout } from "@/layouts/PublicLayout";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
import { RoleBasedRoute } from "@/routes/RoleBasedRoute";

const DashboardPage = lazy(() =>
  import("@/pages/DashboardPage").then((module) => ({ default: module.DashboardPage })),
);
const ForbiddenPage = lazy(() =>
  import("@/pages/ForbiddenPage").then((module) => ({ default: module.ForbiddenPage })),
);
const HomePage = lazy(() =>
  import("@/pages/HomePage").then((module) => ({ default: module.HomePage })),
);
const LoginPage = lazy(() =>
  import("@/pages/LoginPage").then((module) => ({ default: module.LoginPage })),
);
const NearbyNursesPage = lazy(() =>
  import("@/pages/NearbyNursesPage").then((module) => ({ default: module.NearbyNursesPage })),
);
const NotFoundPage = lazy(() =>
  import("@/pages/NotFoundPage").then((module) => ({ default: module.NotFoundPage })),
);
const NotificationsPage = lazy(() =>
  import("@/pages/NotificationsPage").then((module) => ({ default: module.NotificationsPage })),
);
const OfflinePage = lazy(() =>
  import("@/pages/OfflinePage").then((module) => ({ default: module.OfflinePage })),
);
const ProfilePage = lazy(() =>
  import("@/pages/ProfilePage").then((module) => ({ default: module.ProfilePage })),
);
const RatingsPage = lazy(() =>
  import("@/pages/RatingsPage").then((module) => ({ default: module.RatingsPage })),
);
const RegisterNursePage = lazy(() =>
  import("@/pages/RegisterNursePage").then((module) => ({ default: module.RegisterNursePage })),
);
const RegisterPatientPage = lazy(() =>
  import("@/pages/RegisterPatientPage").then((module) => ({ default: module.RegisterPatientPage })),
);
const RequestsPage = lazy(() =>
  import("@/pages/RequestsPage").then((module) => ({ default: module.RequestsPage })),
);
const ServerErrorPage = lazy(() =>
  import("@/pages/ServerErrorPage").then((module) => ({ default: module.ServerErrorPage })),
);
const TrackingPage = lazy(() =>
  import("@/pages/TrackingPage").then((module) => ({ default: module.TrackingPage })),
);
const VerifyPage = lazy(() =>
  import("@/pages/VerifyPage").then((module) => ({ default: module.VerifyPage })),
);
const VisitsPage = lazy(() =>
  import("@/pages/VisitsPage").then((module) => ({ default: module.VisitsPage })),
);

function lazyPage(page: ReactNode): ReactNode {
  return <Suspense fallback={<RouteLoadingState />}>{page}</Suspense>;
}

export const appRoutes: RouteObject[] = [
  {
    element: <PublicLayout />,
    children: [
      { path: "/", element: lazyPage(<HomePage />) },
      { path: "/login", element: lazyPage(<LoginPage />) },
      { path: "/register/patient", element: lazyPage(<RegisterPatientPage />) },
      { path: "/register/nurse", element: lazyPage(<RegisterNursePage />) },
      { path: "/forbidden", element: lazyPage(<ForbiddenPage />) },
      { path: "/offline", element: lazyPage(<OfflinePage />) },
      { path: "/500", element: lazyPage(<ServerErrorPage />) },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/dashboard", element: lazyPage(<DashboardPage />) },
          { path: "/verify", element: lazyPage(<VerifyPage />) },
          {
            element: <RoleBasedRoute roles={["PATIENT", "ADMIN"]} />,
            children: [{ path: "/nurses", element: lazyPage(<NearbyNursesPage />) }],
          },
          { path: "/requests", element: lazyPage(<RequestsPage />) },
          { path: "/tracking", element: lazyPage(<TrackingPage />) },
          { path: "/visits", element: lazyPage(<VisitsPage />) },
          { path: "/ratings", element: lazyPage(<RatingsPage />) },
          { path: "/notifications", element: lazyPage(<NotificationsPage />) },
          { path: "/profile", element: lazyPage(<ProfilePage />) },
        ],
      },
    ],
  },
  { path: "*", element: lazyPage(<NotFoundPage />) },
];
