"""Tracking URL routes."""

from __future__ import annotations

from django.urls import path

from apps.tracking.views import LocationUpdateView, TrackingLocationView

urlpatterns = [
    path("location/update/", LocationUpdateView.as_view(), name="location-update"),
    path("tracking/location/", TrackingLocationView.as_view(), name="tracking-location"),
]
