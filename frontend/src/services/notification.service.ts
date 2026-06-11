import { notificationApi } from "@/api/notification.api";
import type { Notification } from "@/types";

export class NotificationService {
  getNotifications(): Promise<Notification[]> {
    return notificationApi.listNotifications();
  }

  markRead(notificationId: number): Promise<Notification> {
    return notificationApi.markRead(notificationId);
  }

  markAllRead(): Promise<void> {
    return notificationApi.markAllRead();
  }
}

export const notificationService = new NotificationService();
