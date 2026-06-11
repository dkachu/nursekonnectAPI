import type { Notification } from "@/types";

export type NotificationTransportStatus = "idle" | "connecting" | "connected" | "closed" | "error";

export interface NotificationTransport {
  readonly status: NotificationTransportStatus;
  connect: (onNotification: (notification: Notification) => void) => void;
  disconnect: () => void;
}

export class UnsupportedNotificationTransport implements NotificationTransport {
  readonly status: NotificationTransportStatus = "idle";

  connect(onNotification: (notification: Notification) => void): void {
    void onNotification;
  }

  disconnect(): void {
    return;
  }
}

export const notificationTransport = new UnsupportedNotificationTransport();
