import { useCallback, useMemo, useState, type ReactNode } from "react";
import {
  NotificationStoreContext,
  type NotificationStoreValue,
} from "@/stores/notification-store-context";
import type { Notification } from "@/types";

export function NotificationStoreProvider({ children }: { children: ReactNode }): ReactNode {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const markRead = useCallback((notificationId: number): void => {
    setNotifications((items) =>
      items.map((notification) =>
        notification.id === notificationId ? { ...notification, is_read: true } : notification,
      ),
    );
  }, []);

  const markAllRead = useCallback((): void => {
    setNotifications((items) =>
      items.map((notification) => ({
        ...notification,
        is_read: true,
      })),
    );
  }, []);

  const value = useMemo<NotificationStoreValue>(
    () => ({
      notifications,
      unreadCount: notifications.filter((notification) => !notification.is_read).length,
      setNotifications,
      markRead,
      markAllRead,
    }),
    [markAllRead, markRead, notifications],
  );

  return (
    <NotificationStoreContext.Provider value={value}>{children}</NotificationStoreContext.Provider>
  );
}
