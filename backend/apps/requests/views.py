"""Care request API views."""

from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.selectors import PatientProfileSelector
from apps.patients.views import request_ip
from apps.requests.selectors import CareRequestSelector
from apps.requests.serializers import (
    CareRequestCancelSerializer,
    CareRequestCreateSerializer,
    CareRequestSerializer,
)
from apps.requests.services import CareRequestService


def service_error_response(error: ValueError | PermissionError | ObjectDoesNotExist) -> Response:
    """Map service-layer errors to API responses."""
    if isinstance(error, PermissionError):
        return Response({"detail": str(error)}, status=status.HTTP_403_FORBIDDEN)
    return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class CareRequestListCreateView(APIView):
    """List visible care requests and create patient requests."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """List care requests visible to the authenticated user."""
        care_requests = CareRequestSelector().for_actor(request.user)
        return Response(
            CareRequestSerializer(
                care_requests,
                many=True,
                context={"actor": request.user},
            ).data
        )

    def post(self, request: Request) -> Response:
        """Create a care request for the authenticated patient."""
        patient = PatientProfileSelector().get_for_user(request.user)
        serializer = CareRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            care_request = CareRequestService().create(
                actor=request.user,
                patient=patient,
                data=dict(serializer.validated_data),
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError) as error:
            return service_error_response(error)
        return Response(
            CareRequestSerializer(care_request, context={"actor": request.user}).data,
            status=status.HTTP_201_CREATED,
        )


class CareRequestDetailView(APIView):
    """Return a visible care request."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, request_id: int) -> Response:
        """Return request details."""
        care_request = CareRequestSelector().get_for_actor(
            actor=request.user,
            request_id=request_id,
        )
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)


class CareRequestAcceptView(APIView):
    """Accept a pending care request as an eligible nurse."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, request_id: int) -> Response:
        """Accept a care request atomically."""
        try:
            care_request = CareRequestService().accept(
                actor=request.user,
                request_id=request_id,
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)


class CareRequestStartJourneyView(APIView):
    """Start the assigned nurse journey."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, request_id: int) -> Response:
        """Transition request to nurse en route."""
        try:
            care_request = CareRequestService().start_journey(
                actor=request.user,
                request_id=request_id,
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)


class CareRequestArrivedView(APIView):
    """Mark the assigned nurse as arrived."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, request_id: int) -> Response:
        """Transition request to arrived."""
        try:
            care_request = CareRequestService().mark_arrived(
                actor=request.user,
                request_id=request_id,
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)


class CareRequestStartVisitView(APIView):
    """Start the assigned visit."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, request_id: int) -> Response:
        """Transition request to in progress."""
        try:
            care_request = CareRequestService().start_visit(
                actor=request.user,
                request_id=request_id,
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)


class CareRequestCompleteView(APIView):
    """Complete the assigned visit."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, request_id: int) -> Response:
        """Transition request to completed."""
        try:
            care_request = CareRequestService().complete(
                actor=request.user,
                request_id=request_id,
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)


class CareRequestCancelView(APIView):
    """Cancel a care request."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, request_id: int) -> Response:
        """Cancel a non-terminal care request."""
        serializer = CareRequestCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            care_request = CareRequestService().cancel(
                actor=request.user,
                request_id=request_id,
                reason=serializer.validated_data.get("reason", ""),
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(CareRequestSerializer(care_request, context={"actor": request.user}).data)
