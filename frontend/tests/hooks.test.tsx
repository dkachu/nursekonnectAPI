import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { adminService } from "@/services/admin.service";
import { nurseService } from "@/services/nurse.service";
import { trackingService } from "@/services/tracking.service";
import { useAdminNurses } from "@/hooks/useAdmin";
import { useRequestTrackingLocations } from "@/hooks/useLocation";
import { useNearbyNurses } from "@/hooks/useNurses";

function wrapper({ children }: { children: ReactNode }): ReactNode {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("query hooks", () => {
  it("fetches nearby nurses through the service layer", async () => {
    vi.spyOn(nurseService, "getNearbyNurses").mockResolvedValueOnce([
      { id: 2, first_name: "Amina" },
    ]);

    const { result } = renderHook(() => useNearbyNurses(undefined, true), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.[0]?.first_name).toBe("Amina");
  });

  it("fetches admin nurse verification data through the service layer", async () => {
    vi.spyOn(adminService, "listNurses").mockResolvedValueOnce([
      {
        id: 3,
        first_name: "Verifier",
        phone_number: "+254700000000",
        nck_verification_status: "PENDING",
        location_visible: false,
        is_available: false,
        status: "OFFLINE",
      },
    ]);

    const { result } = renderHook(() => useAdminNurses(true), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.[0]?.first_name).toBe("Verifier");
  });

  it("fetches request tracking history through the service layer", async () => {
    vi.spyOn(trackingService, "listRequestLocations").mockResolvedValueOnce([
      {
        id: 4,
        care_request_id: 8,
        latitude: -1.286389,
        longitude: 36.817223,
        recorded_at: "2026-06-11T10:00:00Z",
      },
    ]);

    const { result } = renderHook(() => useRequestTrackingLocations(8), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.[0]?.care_request_id).toBe(8);
  });
});
