"""Patient URL routes."""

from __future__ import annotations

from django.urls import path

from apps.patients.views import (
    EmergencyContactDetailView,
    EmergencyContactListCreateView,
    PatientDependentDetailView,
    PatientDependentListCreateView,
    PatientMedicalInformationView,
    PatientProfileView,
)

urlpatterns = [
    path("patient/profile/", PatientProfileView.as_view(), name="patient-profile"),
    path(
        "patient/emergency-contacts/",
        EmergencyContactListCreateView.as_view(),
        name="patient-emergency-contact-list",
    ),
    path(
        "patient/emergency-contacts/<int:contact_id>/",
        EmergencyContactDetailView.as_view(),
        name="patient-emergency-contact-detail",
    ),
    path(
        "patient/dependents/",
        PatientDependentListCreateView.as_view(),
        name="patient-dependent-list",
    ),
    path(
        "patient/dependents/<int:dependent_id>/",
        PatientDependentDetailView.as_view(),
        name="patient-dependent-detail",
    ),
    path(
        "patients/<int:patient_id>/medical-information/",
        PatientMedicalInformationView.as_view(),
        name="patient-medical-information",
    ),
]
