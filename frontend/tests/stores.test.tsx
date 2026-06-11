import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { NotificationStoreProvider } from "@/stores/notification-store";
import { useNotificationStore } from "@/stores/use-notification-store";

function wrapper({ children }: { children: ReactNode }): ReactNode {
  return <NotificationStoreProvider>{children}</NotificationStoreProvider>;
}

describe("notification store", () => {
  it("derives unread counts from notifications", () => {
    const { result } = renderHook(() => useNotificationStore(), { wrapper });

    act(() => {
      result.current.setNotifications([
        {
          id: 1,
          user: 1,
          notification_type: "JOB_ASSIGNED",
          title: "Assigned",
          message: "A request was assigned.",
          is_read: false,
          created_at: "2026-06-11T00:00:00Z",
        },
      ]);
    });

    expect(result.current.unreadCount).toBe(1);
  });
});
