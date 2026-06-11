import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { notificationService } from "@/services/notification.service";
import { useNotificationStore } from "@/stores/use-notification-store";

export function useNotifications() {
  const store = useNotificationStore();
  const query = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationService.getNotifications(),
  });

  useEffect(() => {
    if (query.data) {
      store.setNotifications(query.data);
    }
  }, [query.data, store]);

  return { ...query, notifications: store.notifications, unreadCount: store.unreadCount };
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  const store = useNotificationStore();
  return useMutation({
    mutationFn: (notificationId: number) => notificationService.markRead(notificationId),
    onSuccess: (notification) => {
      store.markRead(notification.id);
      void queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  const store = useNotificationStore();
  return useMutation<void, Error>({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => {
      store.markAllRead();
      void queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
