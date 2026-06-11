"""Rating URL routes."""

from __future__ import annotations

from django.urls import path

from apps.ratings.views import RatingListCreateView

urlpatterns = [
    path("ratings/", RatingListCreateView.as_view(), name="rating-list"),
]
