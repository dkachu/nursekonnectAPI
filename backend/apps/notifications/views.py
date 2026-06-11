"""Notification API views."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationListView(ListAPIView[Notification]):
    """List notifications for the authenticated user."""

    serializer_class = NotificationSerializer

    def get_queryset(self) -> QuerySet[Notification]:
        """Return only notifications owned by the authenticated user."""
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")


class NotificationUnreadCountView(APIView):
    """Return the authenticated user's unread notification count."""

    def get(self, request: Request) -> Response:
        """Count unread notifications."""
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread_count": unread_count})


class NotificationMarkReadView(APIView):
    """Mark a single notification as read."""

    def post(self, request: Request, notification_id: int) -> Response:
        """Mark an owned notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read", "updated_at"])
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    """Mark all notifications as read for the authenticated user."""

    def post(self, request: Request) -> Response:
        """Mark all owned unread notifications as read."""
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)
        return Response({"updated_count": updated_count})
