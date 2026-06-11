"""Rating API views."""

from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.views import request_ip
from apps.ratings.selectors import RatingSelector
from apps.ratings.serializers import RatingCreateSerializer, RatingSerializer
from apps.ratings.services import RatingService
from apps.requests.views import service_error_response


class RatingListCreateView(APIView):
    """List visible ratings and create patient ratings."""

    def get(self, request: Request) -> Response:
        """List ratings visible to the authenticated actor."""
        ratings = RatingSelector().for_actor(request.user)
        return Response(RatingSerializer(ratings, many=True).data)

    def post(self, request: Request) -> Response:
        """Create a rating for a completed care request."""
        serializer = RatingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rating = RatingService().create(
                actor=request.user,
                data=dict(serializer.validated_data),
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(RatingSerializer(rating).data, status=status.HTTP_201_CREATED)
