import { createContext } from "react";
import type { Notification } from "@/types";

export interface NotificationStoreValue {
  notifications: Notification[];
  unreadCount: number;
  setNotifications: (notifications: Notification[]) => void;
  markRead: (notificationId: number) => void;
  markAllRead: () => void;
}

export const NotificationStoreContext = createContext<NotificationStoreValue | null>(null);
