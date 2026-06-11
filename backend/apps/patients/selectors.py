"""Optimized patient-domain reads."""

from __future__ import annotations

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.patients.models import EmergencyContact, PatientDependent, PatientProfile


class PatientProfileSelector:
    """Read patient profiles with related user data."""

    def get_for_user(self, user: object) -> PatientProfile:
        """Return a patient's own profile."""
        return get_object_or_404(PatientProfile.objects.select_related("user"), user=user)

    def get_by_id(self, patient_id: int) -> PatientProfile:
        """Return a patient profile by primary key."""
        return get_object_or_404(PatientProfile.objects.select_related("user"), id=patient_id)


class EmergencyContactSelector:
    """Read emergency contacts for a patient."""

    def list_for_patient(self, patient: PatientProfile) -> QuerySet[EmergencyContact]:
        """Return emergency contacts for a patient."""
        return patient.emergency_contacts.all()

    def get_for_patient(self, patient: PatientProfile, contact_id: int) -> EmergencyContact:
        """Return a single contact owned by a patient."""
        return get_object_or_404(patient.emergency_contacts, id=contact_id)


class PatientDependentSelector:
    """Read dependents for a patient."""

    def list_for_patient(self, patient: PatientProfile) -> QuerySet[PatientDependent]:
        """Return dependents for a patient."""
        return patient.dependents.all()

    def get_for_patient(self, patient: PatientProfile, dependent_id: int) -> PatientDependent:
        """Return a single dependent owned by a patient."""
        return get_object_or_404(patient.dependents, id=dependent_id)
