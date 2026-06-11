"""Tracking and location API views."""

from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.requests.selectors import CareRequestSelector
from apps.tracking.serializers import (
    LocationUpdateResponseSerializer,
    LocationUpdateSerializer,
    TrackingLocationSerializer,
)
from apps.tracking.selectors import TrackingLocationSelector
from apps.tracking.services.location_updates import LocationUpdateInput, LocationUpdateService


def service_error_response(error: ValueError | PermissionError | ObjectDoesNotExist) -> Response:
    """Map service-layer errors to HTTP responses."""
    if isinstance(error, PermissionError):
        response_status = status.HTTP_403_FORBIDDEN
    elif isinstance(error, ObjectDoesNotExist):
        response_status = status.HTTP_404_NOT_FOUND
    else:
        response_status = status.HTTP_400_BAD_REQUEST
    return Response({"detail": str(error)}, status=response_status)


class LocationUpdateView(APIView):
    """Update the authenticated patient's or nurse's latest GPS location."""

    def post(self, request: Request) -> Response:
        """Persist a browser/mobile GPS update."""
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            profile = LocationUpdateService().update_current_location(
                actor=request.user,
                data=LocationUpdateInput(**serializer.validated_data),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(LocationUpdateResponseSerializer(profile).data)


class TrackingLocationView(APIView):
    """Record a nurse journey tracking GPS point."""

    def post(self, request: Request) -> Response:
        """Persist a nurse tracking location from browser/mobile GPS."""
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tracking_location = LocationUpdateService().record_tracking_location(
                actor=request.user,
                data=LocationUpdateInput(**serializer.validated_data),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(
            TrackingLocationSerializer(tracking_location).data,
            status=status.HTTP_201_CREATED,
        )


class TrackingRequestLocationListView(APIView):
    """List tracking points for a visible assigned care request."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, request_id: int) -> Response:
        """Return recent journey tracking points for patient, assigned nurse, or admin."""
        try:
            care_request = CareRequestSelector().get_for_actor(
                actor=request.user,
                request_id=request_id,
            )
            locations = TrackingLocationSelector().recent_for_request(
                care_request,
                actor=request.user,
            )
        except (PermissionError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(TrackingLocationSerializer(locations, many=True).data)
