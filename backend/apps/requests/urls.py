"""Care request URL routes."""

from __future__ import annotations

from django.urls import path

from apps.requests.views import (
    CareRequestAcceptView,
    CareRequestArrivedView,
    CareRequestCancelView,
    CareRequestCompleteView,
    CareRequestDetailView,
    CareRequestListCreateView,
    CareRequestStartJourneyView,
    CareRequestStartVisitView,
)

urlpatterns = [
    path("requests/", CareRequestListCreateView.as_view(), name="care-request-list"),
    path(
        "requests/<int:request_id>/",
        CareRequestDetailView.as_view(),
        name="care-request-detail",
    ),
    path(
        "requests/<int:request_id>/accept/",
        CareRequestAcceptView.as_view(),
        name="care-request-accept",
    ),
    path(
        "requests/<int:request_id>/start-journey/",
        CareRequestStartJourneyView.as_view(),
        name="care-request-start-journey",
    ),
    path(
        "requests/<int:request_id>/arrived/",
        CareRequestArrivedView.as_view(),
        name="care-request-arrived",
    ),
    path(
        "requests/<int:request_id>/start-visit/",
        CareRequestStartVisitView.as_view(),
        name="care-request-start-visit",
    ),
    path(
        "requests/<int:request_id>/complete/",
        CareRequestCompleteView.as_view(),
        name="care-request-complete",
    ),
    path(
        "requests/<int:request_id>/cancel/",
        CareRequestCancelView.as_view(),
        name="care-request-cancel",
    ),
]
