"""Patient-domain API views."""

from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.permissions import IsPatientMedicalActor, IsPatientUser
from apps.patients.selectors import (
    EmergencyContactSelector,
    PatientDependentSelector,
    PatientProfileSelector,
)
from apps.patients.serializers import (
    EmergencyContactSerializer,
    PatientDependentSerializer,
    PatientMedicalInformationSerializer,
    PatientProfileSerializer,
)
from apps.patients.services.dependents import PatientDependentService
from apps.patients.services.emergency_contacts import EmergencyContactService
from apps.patients.services.profiles import PatientProfileService


def request_ip(request: Request) -> str | None:
    """Return the best-effort client IP address."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class PatientProfileView(APIView):
    """Read and update the authenticated patient's profile."""

    permission_classes = [IsPatientUser]

    def get(self, request: Request) -> Response:
        """Return the authenticated patient's profile."""
        patient = PatientProfileSelector().get_for_user(request.user)
        patient = PatientProfileService().read_profile(
            actor=request.user,
            patient=patient,
            ip_address=request_ip(request),
            include_medical=True,
        )
        return Response(PatientProfileSerializer(patient).data)

    def patch(self, request: Request) -> Response:
        """Partially update the authenticated patient's profile."""
        patient = PatientProfileSelector().get_for_user(request.user)
        serializer = PatientProfileSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = PatientProfileService().update_own_profile(
            actor=request.user,
            patient=patient,
            data=serializer.validated_data,
        )
        return Response(PatientProfileSerializer(patient).data)


class PatientMedicalInformationView(APIView):
    """Read protected medical information for an authorized actor."""

    permission_classes = [IsPatientMedicalActor]

    def get(self, request: Request, patient_id: int) -> Response:
        """Return protected medical information when authorized."""
        patient = PatientProfileSelector().get_by_id(patient_id)
        patient = PatientProfileService().read_medical_information(
            actor=request.user,
            patient=patient,
            ip_address=request_ip(request),
        )
        return Response(PatientMedicalInformationSerializer(patient).data)


class EmergencyContactListCreateView(APIView):
    """List and create emergency contacts."""

    permission_classes = [IsPatientUser]

    def get(self, request: Request) -> Response:
        """List emergency contacts for the authenticated patient."""
        patient = PatientProfileSelector().get_for_user(request.user)
        contacts = EmergencyContactSelector().list_for_patient(patient)
        return Response(EmergencyContactSerializer(contacts, many=True).data)

    def post(self, request: Request) -> Response:
        """Create an emergency contact for the authenticated patient."""
        patient = PatientProfileSelector().get_for_user(request.user)
        serializer = EmergencyContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = EmergencyContactService().create(
            actor=request.user,
            patient=patient,
            data=serializer.validated_data,
        )
        return Response(EmergencyContactSerializer(contact).data, status=status.HTTP_201_CREATED)


class EmergencyContactDetailView(APIView):
    """Update and delete emergency contacts."""

    permission_classes = [IsPatientUser]

    def patch(self, request: Request, contact_id: int) -> Response:
        """Partially update an emergency contact."""
        patient = PatientProfileSelector().get_for_user(request.user)
        contact = EmergencyContactSelector().get_for_patient(patient, contact_id)
        serializer = EmergencyContactSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        contact = EmergencyContactService().update(
            actor=request.user,
            patient=patient,
            contact=contact,
            data=serializer.validated_data,
        )
        return Response(EmergencyContactSerializer(contact).data)

    def delete(self, request: Request, contact_id: int) -> Response:
        """Delete an emergency contact."""
        patient = PatientProfileSelector().get_for_user(request.user)
        contact = EmergencyContactSelector().get_for_patient(patient, contact_id)
        EmergencyContactService().delete(actor=request.user, patient=patient, contact=contact)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientDependentListCreateView(APIView):
    """List and create patient dependents."""

    permission_classes = [IsPatientUser]

    def get(self, request: Request) -> Response:
        """List dependents for the authenticated patient."""
        patient = PatientProfileSelector().get_for_user(request.user)
        dependents = PatientDependentSelector().list_for_patient(patient)
        return Response(PatientDependentSerializer(dependents, many=True).data)

    def post(self, request: Request) -> Response:
        """Create a dependent for the authenticated patient."""
        patient = PatientProfileSelector().get_for_user(request.user)
        serializer = PatientDependentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dependent = PatientDependentService().create(
            actor=request.user,
            patient=patient,
            data=serializer.validated_data,
        )
        return Response(PatientDependentSerializer(dependent).data, status=status.HTTP_201_CREATED)


class PatientDependentDetailView(APIView):
    """Update and delete patient dependents."""

    permission_classes = [IsPatientUser]

    def patch(self, request: Request, dependent_id: int) -> Response:
        """Partially update a dependent."""
        patient = PatientProfileSelector().get_for_user(request.user)
        dependent = PatientDependentSelector().get_for_patient(patient, dependent_id)
        serializer = PatientDependentSerializer(dependent, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        dependent = PatientDependentService().update(
            actor=request.user,
            patient=patient,
            dependent=dependent,
            data=serializer.validated_data,
        )
        return Response(PatientDependentSerializer(dependent).data)

    def delete(self, request: Request, dependent_id: int) -> Response:
        """Delete a dependent."""
        patient = PatientProfileSelector().get_for_user(request.user)
        dependent = PatientDependentSelector().get_for_patient(patient, dependent_id)
        PatientDependentService().delete(actor=request.user, patient=patient, dependent=dependent)
        return Response(status=status.HTTP_204_NO_CONTENT)
