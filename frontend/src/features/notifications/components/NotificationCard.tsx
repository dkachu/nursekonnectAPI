import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Notification } from "@/types";

export function NotificationCard({
  notification,
  onMarkRead,
  isUpdating = false,
}: {
  notification: Notification;
  onMarkRead?: (notificationId: number) => void;
  isUpdating?: boolean;
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <CardTitle>{notification.title}</CardTitle>
          <Badge variant={notification.is_read ? "neutral" : "default"}>
            {notification.is_read ? "Read" : "Unread"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 text-sm text-muted-foreground">
        <p>{notification.message}</p>
        {!notification.is_read && onMarkRead ? (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onMarkRead(notification.id)}
            disabled={isUpdating}
          >
            {isUpdating ? "Updating" : "Mark as Read"}
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}
