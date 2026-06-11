import { describe, expect, it, vi } from "vitest";
import { adminApi } from "@/api/admin.api";
import { nurseApi } from "@/api/nurse.api";
import { trackingApi } from "@/api/tracking.api";
import { AdminService } from "@/services/admin.service";
import { NurseService } from "@/services/nurse.service";
import { TrackingService } from "@/services/tracking.service";

describe("NurseService", () => {
  it("delegates nearby nurse discovery to the API layer", async () => {
    const nurses = [{ id: 1, first_name: "Jane", is_available: true }];
    const spy = vi.spyOn(nurseApi, "getNearbyNurses").mockResolvedValueOnce(nurses);
    const service = new NurseService();

    await expect(
      service.getNearbyNurses({ specialization: "WOUND_CARE", limit: 5 }),
    ).resolves.toEqual(nurses);
    expect(spy).toHaveBeenCalledWith({ specialization: "WOUND_CARE", limit: 5 });
  });
});

describe("AdminService", () => {
  it("loads admin nurse dashboard data from the API layer", async () => {
    const nurses = [{ id: 5, first_name: "Admin", phone_number: "+254700000000" }];
    const spy = vi.spyOn(adminApi, "listNurses").mockResolvedValueOnce(nurses as never);
    const service = new AdminService();

    await expect(service.listNurses()).resolves.toEqual(nurses);
    expect(spy).toHaveBeenCalledOnce();
  });

  it("reviews nurse credentials through the existing admin API", async () => {
    const credential = {
      id: 7,
      credential_type: "NCK_LICENSE",
      image: "/license.png",
      verification_status: "VERIFIED",
    };
    const spy = vi.spyOn(adminApi, "reviewCredential").mockResolvedValueOnce(credential as never);
    const service = new AdminService();

    await expect(
      service.reviewCredential(5, 7, {
        verification_status: "VERIFIED",
        review_notes: "Valid credential.",
      }),
    ).resolves.toEqual(credential);
    expect(spy).toHaveBeenCalledWith(5, 7, {
      verification_status: "VERIFIED",
      review_notes: "Valid credential.",
    });
  });
});

describe("TrackingService", () => {
  it("loads request-scoped tracking history from the API layer", async () => {
    const locations = [{ id: 9, care_request_id: 3, recorded_at: "2026-06-11T10:00:00Z" }];
    const spy = vi.spyOn(trackingApi, "listRequestLocations").mockResolvedValueOnce(locations);
    const service = new TrackingService();

    await expect(service.listRequestLocations(3)).resolves.toEqual(locations);
    expect(spy).toHaveBeenCalledWith(3);
  });
});
