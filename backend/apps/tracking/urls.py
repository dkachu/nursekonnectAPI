"""Tracking URL routes."""

from __future__ import annotations

from django.urls import path

from apps.tracking.views import (
    LocationUpdateView,
    TrackingLocationView,
    TrackingRequestLocationListView,
)

urlpatterns = [
    path("location/update/", LocationUpdateView.as_view(), name="location-update"),
    path("tracking/location/", TrackingLocationView.as_view(), name="tracking-location"),
    path(
        "tracking/requests/<int:request_id>/locations/",
        TrackingRequestLocationListView.as_view(),
        name="tracking-request-location-list",
    ),
]
