import { Outlet } from "react-router-dom";
import type { ReactNode } from "react";
import { Footer } from "@/components/layout/Footer";
import { NetworkStatusBanner } from "@/components/layout/NetworkStatusBanner";
import { TopNavigation } from "@/components/layout/TopNavigation";

export function PublicLayout(): ReactNode {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <TopNavigation />
      <NetworkStatusBanner />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
