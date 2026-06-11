"""Nurse-domain API views."""

from __future__ import annotations

from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsPatient
from apps.nurses.models import NurseSpecialization
from apps.nurses.permissions import IsAuthorizedAdmin, IsNurseUser
from apps.nurses.selectors import (
    NurseAvailabilitySelector,
    NurseCredentialSelector,
    NurseProfileSelector,
)
from apps.nurses.serializers import (
    NearbyNurseQuerySerializer,
    NearbyNurseResultSerializer,
    NurseAvailabilitySlotSerializer,
    NurseCredentialReviewSerializer,
    NurseCredentialSerializer,
    NurseProfileSerializer,
    NurseSpecializationSerializer,
    NurseSpecializationUpdateSerializer,
    NurseStatusSerializer,
    NurseVerificationSerializer,
)
from apps.nurses.services.availability import NurseAvailabilityService
from apps.nurses.services.credentials import NurseCredentialService
from apps.nurses.services.discovery import NearbyNurseDiscoveryService
from apps.nurses.services.nck import NCKVerificationPortalService
from apps.nurses.services.profiles import NurseProfileService
from apps.nurses.services.reputation import NurseReputationService
from apps.nurses.services.specializations import NurseSpecializationService
from apps.nurses.services.status import NurseStatusService
from apps.nurses.services.verification import NurseVerificationService


def service_error_response(error: ValueError | PermissionError) -> Response:
    """Map service-level errors to API responses."""
    response_status = (
        status.HTTP_403_FORBIDDEN
        if isinstance(error, PermissionError)
        else status.HTTP_400_BAD_REQUEST
    )
    return Response({"detail": str(error)}, status=response_status)


class NurseProfileView(APIView):
    """Read and update the authenticated nurse's profile."""

    permission_classes = [IsNurseUser]

    def get(self, request: Request) -> Response:
        """Return the authenticated nurse's profile."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        return Response(NurseProfileSerializer(nurse).data)

    def patch(self, request: Request) -> Response:
        """Partially update the authenticated nurse's profile."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        serializer = NurseProfileSerializer(nurse, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            nurse = NurseProfileService().update_own_profile(
                actor=request.user,
                nurse=nurse,
                data=serializer.validated_data,
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseProfileSerializer(nurse).data)


class NearbyNurseListView(APIView):
    """Return road-distance ranked nearby nurses for an authenticated patient."""

    permission_classes = [IsPatient]

    def get(self, request: Request) -> Response:
        """Discover nearby eligible nurses using PostGIS and OSRM."""
        serializer = NearbyNurseQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            results = NearbyNurseDiscoveryService().discover(
                patient=request.user.patient_profile,
                specialization_code=serializer.validated_data.get("specialization"),
                limit=serializer.validated_data["limit"],
            )
        except ValueError as error:
            return service_error_response(error)
        return Response(NearbyNurseResultSerializer(results, many=True).data)


class NCKVerificationPortalRedirectView(APIView):
    """Redirect users to the official NCK license status portal."""

    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> HttpResponseRedirect:
        """Redirect to the configured NCK license verification page."""
        return HttpResponseRedirect(NCKVerificationPortalService().verification_url())


class NurseSpecializationListView(APIView):
    """List supported nurse specializations."""

    permission_classes = [IsNurseUser]

    def get(self, request: Request) -> Response:
        """Return supported specializations."""
        specializations = NurseSpecialization.objects.all()
        return Response(NurseSpecializationSerializer(specializations, many=True).data)


class NurseSpecializationUpdateView(APIView):
    """Update the authenticated nurse's specialization set."""

    permission_classes = [IsNurseUser]

    def put(self, request: Request) -> Response:
        """Replace the nurse's specialization set."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        serializer = NurseSpecializationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            nurse = NurseSpecializationService().set_specializations(
                actor=request.user,
                nurse=nurse,
                codes=serializer.validated_data["specializations"],
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseProfileSerializer(nurse).data)


class NurseCredentialListCreateView(APIView):
    """List and create nurse credential uploads."""

    permission_classes = [IsNurseUser]

    def get(self, request: Request) -> Response:
        """List credentials for the authenticated nurse."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        credentials = NurseCredentialSelector().list_for_nurse(nurse)
        return Response(NurseCredentialSerializer(credentials, many=True).data)

    def post(self, request: Request) -> Response:
        """Upload a credential image for the authenticated nurse."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        serializer = NurseCredentialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            credential = NurseCredentialService().create(
                actor=request.user,
                nurse=nurse,
                data=serializer.validated_data,
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseCredentialSerializer(credential).data, status=status.HTTP_201_CREATED)


class NurseAvailabilityListCreateView(APIView):
    """List and create availability slots."""

    permission_classes = [IsNurseUser]

    def get(self, request: Request) -> Response:
        """List availability slots for the authenticated nurse."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        slots = NurseAvailabilitySelector().list_for_nurse(nurse)
        return Response(NurseAvailabilitySlotSerializer(slots, many=True).data)

    def post(self, request: Request) -> Response:
        """Create an availability slot for the authenticated nurse."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        serializer = NurseAvailabilitySlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            slot = NurseAvailabilityService().create(
                actor=request.user,
                nurse=nurse,
                data=serializer.validated_data,
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseAvailabilitySlotSerializer(slot).data, status=status.HTTP_201_CREATED)


class NurseAvailabilityDetailView(APIView):
    """Update and delete availability slots."""

    permission_classes = [IsNurseUser]

    def patch(self, request: Request, slot_id: int) -> Response:
        """Partially update an availability slot."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        slot = NurseAvailabilitySelector().get_for_nurse(nurse, slot_id)
        serializer = NurseAvailabilitySlotSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            slot = NurseAvailabilityService().update(
                actor=request.user,
                nurse=nurse,
                slot=slot,
                data=serializer.validated_data,
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseAvailabilitySlotSerializer(slot).data)

    def delete(self, request: Request, slot_id: int) -> Response:
        """Delete an availability slot."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        slot = NurseAvailabilitySelector().get_for_nurse(nurse, slot_id)
        try:
            NurseAvailabilityService().delete(actor=request.user, nurse=nurse, slot=slot)
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NurseStatusView(APIView):
    """Update nurse online, busy, or offline status."""

    permission_classes = [IsNurseUser]

    def post(self, request: Request) -> Response:
        """Update operational nurse status."""
        nurse = NurseProfileSelector().get_for_user(request.user)
        serializer = NurseStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            nurse = NurseStatusService().update_status(
                actor=request.user,
                nurse=nurse,
                status=serializer.validated_data["status"],
                location_visible=serializer.validated_data.get("location_visible"),
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseProfileSerializer(nurse).data)


class AdminNurseVerificationView(APIView):
    """Update NCK verification state for a nurse."""

    permission_classes = [IsAuthorizedAdmin]

    def patch(self, request: Request, nurse_id: int) -> Response:
        """Apply an administrator NCK verification decision."""
        nurse = NurseProfileSelector().get_by_id(nurse_id)
        serializer = NurseVerificationSerializer(nurse, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            nurse = NurseVerificationService().update_verification(
                actor=request.user,
                nurse=nurse,
                data=serializer.validated_data,
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseProfileSerializer(nurse).data)


class AdminNurseListView(APIView):
    """List nurse profiles for administrator verification workflows."""

    permission_classes = [IsAuthorizedAdmin]

    def get(self, request: Request) -> Response:
        """Return nurse profiles visible to authorized administrators."""
        nurses = NurseProfileSelector().list_for_admin()
        return Response(NurseProfileSerializer(nurses, many=True).data)


class AdminNurseCredentialListView(APIView):
    """List uploaded credentials for an administrator-selected nurse."""

    permission_classes = [IsAuthorizedAdmin]

    def get(self, request: Request, nurse_id: int) -> Response:
        """Return credentials for a nurse under review."""
        nurse = NurseProfileSelector().get_by_id(nurse_id)
        credentials = NurseCredentialSelector().list_for_nurse(nurse)
        return Response(NurseCredentialSerializer(credentials, many=True).data)


class AdminNurseCredentialReviewView(APIView):
    """Review an uploaded nurse credential."""

    permission_classes = [IsAuthorizedAdmin]

    def patch(self, request: Request, nurse_id: int, credential_id: int) -> Response:
        """Apply an administrator credential review decision."""
        nurse = NurseProfileSelector().get_by_id(nurse_id)
        credential = NurseCredentialSelector().get_for_nurse(nurse, credential_id)
        serializer = NurseCredentialReviewSerializer(credential, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            credential = NurseCredentialService().review(
                actor=request.user,
                credential=credential,
                data=serializer.validated_data,
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(NurseCredentialSerializer(credential).data)


class AdminNurseReputationRecalculateView(APIView):
    """Recalculate a nurse reputation score."""

    permission_classes = [IsAuthorizedAdmin]

    def post(self, request: Request, nurse_id: int) -> Response:
        """Recalculate and return the nurse's reputation score."""
        nurse = NurseProfileSelector().get_by_id(nurse_id)
        nurse = NurseReputationService().recalculate(nurse=nurse)
        return Response(NurseProfileSerializer(nurse).data)
