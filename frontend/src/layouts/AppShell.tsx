import { Outlet } from "react-router-dom";
import type { ReactNode } from "react";
import { Footer } from "@/components/layout/Footer";
import { MobileNavigation } from "@/components/layout/MobileNavigation";
import { NetworkStatusBanner } from "@/components/layout/NetworkStatusBanner";
import { SessionExpiryBanner } from "@/components/layout/SessionExpiryBanner";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNavigation } from "@/components/layout/TopNavigation";

export function AppShell(): ReactNode {
  return (
    <div className="min-h-screen bg-background">
      <div className="lg:hidden">
        <TopNavigation />
      </div>
      <NetworkStatusBanner />
      <SessionExpiryBanner />
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <main className="flex-1 px-4 py-6 pb-24 sm:px-6 lg:px-8 lg:py-8">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
          <Footer />
        </div>
      </div>
      <MobileNavigation />
    </div>
  );
}
