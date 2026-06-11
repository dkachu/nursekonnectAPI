import { apiClient } from "@/api/client";
import type { Notification, NotificationListResponse } from "@/types";

function unwrapNotifications(payload: Notification[] | NotificationListResponse): Notification[] {
  return Array.isArray(payload) ? payload : payload.results;
}

export const notificationApi = {
  async listNotifications(): Promise<Notification[]> {
    const response = await apiClient.get<Notification[] | NotificationListResponse>(
      "/api/notifications/",
    );
    return unwrapNotifications(response.data);
  },
  async markRead(notificationId: number): Promise<Notification> {
    const response = await apiClient.post<Notification>(
      `/api/notifications/${notificationId}/mark-read/`,
    );
    return response.data;
  },
  async markAllRead(): Promise<void> {
    await apiClient.post("/api/notifications/mark-all-read/");
  },
};
