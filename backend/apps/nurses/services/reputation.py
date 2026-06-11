"""Nurse reputation scoring service."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.nurses.models import NurseProfile


class NurseReputationService:
    """Calculate and persist nurse reputation scores."""

    @transaction.atomic
    def recalculate(self, *, nurse: NurseProfile) -> NurseProfile:
        """Recalculate reputation from rating, completion, cancellation, and response speed."""
        total_outcomes = nurse.completed_visits_count + nurse.cancelled_visits_count
        completion_rate = (
            Decimal(nurse.completed_visits_count) / Decimal(total_outcomes)
            if total_outcomes
            else Decimal("0")
        )
        response_score = self._response_score(nurse.average_response_seconds)
        rating_score = Decimal(nurse.rating) / Decimal("5")
        score = (
            rating_score * Decimal("45")
            + completion_rate * Decimal("35")
            + response_score * Decimal("20")
        )
        nurse.reputation_score = score.quantize(Decimal("0.01"))
        nurse.save(update_fields=["reputation_score", "updated_at"])
        return nurse

    def _response_score(self, average_response_seconds: int) -> Decimal:
        """Return a normalized response speed score."""
        if average_response_seconds <= 0:
            return Decimal("0")
        if average_response_seconds <= 60:
            return Decimal("1")
        if average_response_seconds >= 600:
            return Decimal("0")
        return Decimal(600 - average_response_seconds) / Decimal(540)
