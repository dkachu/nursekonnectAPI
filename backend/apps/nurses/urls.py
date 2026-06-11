"""Nurse URL routes."""

from __future__ import annotations

from django.urls import path

from apps.nurses.views import (
    AdminNurseCredentialListView,
    AdminNurseCredentialReviewView,
    AdminNurseListView,
    AdminNurseReputationRecalculateView,
    AdminNurseVerificationView,
    NCKVerificationPortalRedirectView,
    NearbyNurseListView,
    NurseAvailabilityDetailView,
    NurseAvailabilityListCreateView,
    NurseCredentialListCreateView,
    NurseProfileView,
    NurseSpecializationListView,
    NurseSpecializationUpdateView,
    NurseStatusView,
)

urlpatterns = [
    path(
        "nurses/nck-license-status/",
        NCKVerificationPortalRedirectView.as_view(),
        name="nck-license-status-redirect",
    ),
    path("nurses/nearby/", NearbyNurseListView.as_view(), name="nearby-nurses"),
    path("nurse/profile/", NurseProfileView.as_view(), name="nurse-profile"),
    path(
        "nurse/specializations/",
        NurseSpecializationListView.as_view(),
        name="nurse-specialization-list",
    ),
    path(
        "nurse/profile/specializations/",
        NurseSpecializationUpdateView.as_view(),
        name="nurse-specialization-update",
    ),
    path(
        "nurse/credentials/",
        NurseCredentialListCreateView.as_view(),
        name="nurse-credential-list",
    ),
    path(
        "nurse/availability/",
        NurseAvailabilityListCreateView.as_view(),
        name="nurse-availability-list",
    ),
    path(
        "nurse/availability/<int:slot_id>/",
        NurseAvailabilityDetailView.as_view(),
        name="nurse-availability-detail",
    ),
    path("nurse/status/", NurseStatusView.as_view(), name="nurse-status"),
    path(
        "admin/nurses/",
        AdminNurseListView.as_view(),
        name="admin-nurse-list",
    ),
    path(
        "admin/nurses/<int:nurse_id>/credentials/",
        AdminNurseCredentialListView.as_view(),
        name="admin-nurse-credential-list",
    ),
    path(
        "admin/nurses/<int:nurse_id>/verification/",
        AdminNurseVerificationView.as_view(),
        name="admin-nurse-verification",
    ),
    path(
        "admin/nurses/<int:nurse_id>/credentials/<int:credential_id>/review/",
        AdminNurseCredentialReviewView.as_view(),
        name="admin-nurse-credential-review",
    ),
    path(
        "admin/nurses/<int:nurse_id>/reputation/recalculate/",
        AdminNurseReputationRecalculateView.as_view(),
        name="admin-nurse-reputation-recalculate",
    ),
]
