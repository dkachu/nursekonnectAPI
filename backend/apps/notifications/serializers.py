"""Notification API serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer[Notification]):
    """Serialize in-app notifications for the authenticated recipient."""

    user = serializers.IntegerField(source="recipient_id", read_only=True)
    message = serializers.CharField(source="body", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "user",
            "notification_type",
            "title",
            "message",
            "is_read",
            "payload",
            "resource",
            "resource_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
