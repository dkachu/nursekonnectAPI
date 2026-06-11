"""Notification API tests."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.notifications.models import Notification, NotificationType

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


@pytest.fixture
def user() -> object:
    """Create an authenticated patient user."""
    return User.objects.create_user(
        email="notify-patient@example.com",
        password="StrongPassword123!",
        first_name="Notify",
        last_name="Patient",
        role=UserRole.PATIENT,
    )


@pytest.mark.django_db
def test_user_lists_only_owned_notifications(api_client: APIClient, user: object) -> None:
    """Notification list is scoped to the authenticated recipient."""
    other_user = User.objects.create_user(
        email="other@example.com",
        password="StrongPassword123!",
        first_name="Other",
        last_name="User",
        role=UserRole.PATIENT,
    )
    owned = Notification.objects.create(
        recipient=user,
        notification_type=NotificationType.JOB_ACCEPTED,
        title="Request accepted",
        body="A nurse accepted your request.",
    )
    Notification.objects.create(
        recipient=other_user,
        notification_type=NotificationType.JOB_CANCELLED,
        title="Other notification",
        body="Not visible.",
    )
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("notification-list"))

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == owned.id
    assert response.data["results"][0]["message"] == owned.body


@pytest.mark.django_db
def test_mark_notification_read_enforces_ownership(
    api_client: APIClient,
    user: object,
) -> None:
    """Users cannot mark another recipient's notification as read."""
    other_user = User.objects.create_user(
        email="notification-owner@example.com",
        password="StrongPassword123!",
        first_name="Owner",
        last_name="User",
        role=UserRole.NURSE,
    )
    notification = Notification.objects.create(
        recipient=other_user,
        notification_type=NotificationType.JOB_ASSIGNED,
        title="Private",
        body="Private notification.",
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(reverse("notification-mark-read", args=[notification.id]))

    assert response.status_code == 404
    notification.refresh_from_db()
    assert notification.is_read is False


@pytest.mark.django_db
def test_unread_count_and_mark_all_read(api_client: APIClient, user: object) -> None:
    """Unread count and mark-all operate only on the authenticated user's notifications."""
    Notification.objects.create(
        recipient=user,
        notification_type=NotificationType.NURSE_EN_ROUTE,
        title="En route",
        body="Your nurse is on the way.",
    )
    Notification.objects.create(
        recipient=user,
        notification_type=NotificationType.NURSE_ARRIVED,
        title="Arrived",
        body="Your nurse has arrived.",
    )
    api_client.force_authenticate(user=user)

    count_response = api_client.get(reverse("notification-unread-count"))
    mark_all_response = api_client.post(reverse("notification-mark-all-read"))

    assert count_response.status_code == 200
    assert count_response.data["unread_count"] == 2
    assert mark_all_response.status_code == 200
    assert mark_all_response.data["updated_count"] == 2
    assert Notification.objects.filter(recipient=user, is_read=False).count() == 0
