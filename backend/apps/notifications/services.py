"""Notification services."""

from __future__ import annotations

from typing import Any

from apps.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationType,
)


class NotificationService:
    """Persist notification events for downstream delivery workers."""

    def notify(
        self,
        *,
        recipient: object,
        notification_type: str,
        title: str,
        body: str,
        payload: dict[str, Any],
        resource: str,
        resource_id: str | int,
        channel: str = NotificationChannel.PUSH,
    ) -> Notification:
        """Create a notification event."""
        if notification_type not in NotificationType.values:
            raise ValueError("Unsupported notification type.")
        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            channel=channel,
            title=title,
            body=body,
            payload=payload,
            resource=resource,
            resource_id=str(resource_id),
        )
