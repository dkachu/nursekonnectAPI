import type { ReactNode } from "react";
import { getApiErrorMessage } from "@/api/client";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { NotificationCard } from "@/features/notifications/components/NotificationCard";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "@/hooks/useNotifications";

export function NotificationsPage(): ReactNode {
  const { notifications, unreadCount, refetch, isLoading, error } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        description="Request, journey, visit, and account updates."
        actions={
          unreadCount > 0 ? (
            <Button
              variant="outline"
              onClick={() => void markAllRead.mutateAsync()}
              disabled={markAllRead.isPending}
            >
              Mark All Read
            </Button>
          ) : undefined
        }
      />
      {isLoading ? <LoadingState /> : null}
      {error ? (
        <ErrorState message={getApiErrorMessage(error)} onRetry={() => void refetch()} />
      ) : null}
      {markRead.error ? <ErrorState message={getApiErrorMessage(markRead.error)} /> : null}
      {markAllRead.error ? <ErrorState message={getApiErrorMessage(markAllRead.error)} /> : null}
      {notifications.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {notifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onMarkRead={(notificationId) => void markRead.mutateAsync(notificationId)}
              isUpdating={markRead.isPending}
            />
          ))}
        </div>
      ) : null}
      {!isLoading && notifications.length === 0 ? (
        <EmptyState
          title="No Notifications"
          message="Important care workflow updates will be listed here."
          action={
            <Button variant="outline" onClick={() => void refetch()}>
              Refresh
            </Button>
          }
        />
      ) : null}
    </div>
  );
}
