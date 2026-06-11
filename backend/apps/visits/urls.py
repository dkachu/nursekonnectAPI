"""Visit note URL routes."""

from __future__ import annotations

from django.urls import path

from apps.visits.views import VisitNoteDetailView, VisitNoteListCreateView

urlpatterns = [
    path("visit-notes/", VisitNoteListCreateView.as_view(), name="visit-note-list"),
    path(
        "visit-notes/<int:note_id>/",
        VisitNoteDetailView.as_view(),
        name="visit-note-detail",
    ),
]
