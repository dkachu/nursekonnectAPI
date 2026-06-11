"""Visit note API views."""

from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.views import request_ip
from apps.requests.views import service_error_response
from apps.visits.permissions import IsVisitMedicalActor
from apps.visits.selectors import VisitNoteSelector
from apps.visits.serializers import (
    VisitNoteCreateSerializer,
    VisitNoteSerializer,
    VisitNoteUpdateSerializer,
)
from apps.visits.services import VisitNoteService


class VisitNoteListCreateView(APIView):
    """List visible visit notes and create assigned-nurse notes."""

    permission_classes = [IsVisitMedicalActor]

    def get(self, request: Request) -> Response:
        """List visit notes visible to the authenticated actor."""
        notes = list(VisitNoteSelector().for_actor(request.user))
        VisitNoteService().log_list_read(
            actor=request.user,
            notes=notes,
            ip_address=request_ip(request),
        )
        return Response(VisitNoteSerializer(notes, many=True).data)

    def post(self, request: Request) -> Response:
        """Create visit notes for an in-progress assigned visit."""
        serializer = VisitNoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            note = VisitNoteService().create(
                actor=request.user,
                data=dict(serializer.validated_data),
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(VisitNoteSerializer(note).data, status=status.HTTP_201_CREATED)


class VisitNoteDetailView(APIView):
    """Read and update a protected visit note."""

    permission_classes = [IsVisitMedicalActor]

    def get(self, request: Request, note_id: int) -> Response:
        """Return a visible visit note."""
        note = VisitNoteSelector().get_for_actor(actor=request.user, note_id=note_id)
        note = VisitNoteService().read(
            actor=request.user,
            note=note,
            ip_address=request_ip(request),
        )
        return Response(VisitNoteSerializer(note).data)

    def patch(self, request: Request, note_id: int) -> Response:
        """Update a visit note as the assigned nurse."""
        note = VisitNoteSelector().get_for_actor(actor=request.user, note_id=note_id)
        serializer = VisitNoteUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            note = VisitNoteService().update(
                actor=request.user,
                note=note,
                data=dict(serializer.validated_data),
                ip_address=request_ip(request),
            )
        except (PermissionError, ValueError, ObjectDoesNotExist) as error:
            return service_error_response(error)
        return Response(VisitNoteSerializer(note).data)
