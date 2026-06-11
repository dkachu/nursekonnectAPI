"""Intelligent nurse matching services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import NotificationType
from apps.notifications.services import NotificationService
from apps.nurses.models import NurseProfile
from apps.nurses.services.discovery import OSRMRouteError, OSRMRouteService, RouteEstimate
from apps.requests.models import CareRequest, RequestOffer, RequestOfferStatus
from apps.tracking.selectors import LocationSelector

SERVICE_SPECIALIZATION_MAP = {
    "GENERAL_NURSING": "GENERAL_NURSING",
    "WOUND_CARE": "WOUND_CARE",
    "ELDERLY_CARE": "GERIATRIC_CARE",
    "PALLIATIVE_CARE": "PALLIATIVE_CARE",
    "POST_SURGERY_CARE": "POST_SURGICAL_CARE",
    "MATERNITY_CARE": "MIDWIFERY",
    "CHRONIC_DISEASE_SUPPORT": "CHRONIC_DISEASE_SUPPORT",
}


@dataclass(frozen=True)
class NurseMatchCandidate:
    """A route-scored nurse candidate for request matching."""

    nurse: NurseProfile
    distance_km: float
    estimated_travel_time: int
    specialization_match: bool
    radius_km: int


@dataclass(frozen=True)
class MatchingResult:
    """Summary of a matching distribution pass."""

    care_request: CareRequest
    notified_count: int
    final_radius_km: int | None


class RankingService:
    """Rank eligible nurse candidates for care request distribution."""

    def rank(self, candidates: list[NurseMatchCandidate]) -> list[NurseMatchCandidate]:
        """Return candidates ranked by distance, specialization, reputation, response speed."""
        return sorted(candidates, key=self._ranking_key)

    def _ranking_key(self, candidate: NurseMatchCandidate) -> tuple[float, bool, Decimal, int]:
        """Return the deterministic matching ranking key."""
        response_speed = (
            candidate.nurse.average_response_seconds
            if candidate.nurse.average_response_seconds > 0
            else 999999
        )
        return (
            candidate.distance_km,
            not candidate.specialization_match,
            -candidate.nurse.reputation_score,
            response_speed,
        )


class MatchingService:
    """Find, rank, offer, and notify a bounded set of eligible nurses."""

    def __init__(
        self,
        *,
        route_service: OSRMRouteService | None = None,
        ranking_service: RankingService | None = None,
        notification_service: NotificationService | None = None,
        location_selector: LocationSelector | None = None,
    ) -> None:
        self.route_service = route_service or OSRMRouteService()
        self.ranking_service = ranking_service or RankingService()
        self.notification_service = notification_service or NotificationService()
        self.location_selector = location_selector or LocationSelector()

    @transaction.atomic
    def match_and_notify(self, *, care_request: CareRequest) -> MatchingResult:
        """Notify up to the nearest configured number of eligible nurses."""
        if care_request.location is None:
            raise ValueError("Care request location is required for matching.")

        batch_size = settings.MATCHING_NOTIFICATION_BATCH_SIZE
        notified_count = RequestOffer.objects.filter(
            care_request=care_request,
            status=RequestOfferStatus.OFFERED,
        ).count()
        excluded_nurse_ids = set(
            RequestOffer.objects.filter(care_request=care_request).values_list(
                "nurse_id", flat=True
            )
        )
        final_radius_km: int | None = None

        for radius_km in settings.MATCHING_RADIUS_STEPS_KM:
            if notified_count >= batch_size:
                break

            candidates = self._eligible_candidates(
                care_request=care_request,
                radius_km=radius_km,
                excluded_nurse_ids=excluded_nurse_ids,
            )
            ranked_candidates = self.ranking_service.rank(candidates)

            for candidate in ranked_candidates:
                if notified_count >= batch_size:
                    break
                offer = self._create_offer(
                    care_request=care_request,
                    candidate=candidate,
                    rank=notified_count + 1,
                )
                self._notify_nurse(offer=offer, candidate=candidate)
                excluded_nurse_ids.add(candidate.nurse.id)
                notified_count += 1
                final_radius_km = radius_km

        return MatchingResult(
            care_request=care_request,
            notified_count=notified_count,
            final_radius_km=final_radius_km,
        )

    def _eligible_candidates(
        self,
        *,
        care_request: CareRequest,
        radius_km: int,
        excluded_nurse_ids: set[int],
    ) -> list[NurseMatchCandidate]:
        """Return route-scored candidates within platform and nurse constraints."""
        specialization_code = self.specialization_for_service(care_request.service_type)
        candidates: list[NurseMatchCandidate] = []
        queryset = self.location_selector.candidate_nurses_within_radius(
            origin=care_request.location,
            radius_km=radius_km,
        ).exclude(id__in=excluded_nurse_ids)[: settings.NEARBY_NURSE_CANDIDATE_LIMIT]

        for nurse in queryset:
            if not self._has_specialization(nurse=nurse, specialization_code=specialization_code):
                continue
            if nurse.current_location is None:
                continue
            try:
                estimate = self.route_service.route(
                    origin=care_request.location,
                    destination=nurse.current_location,
                )
            except OSRMRouteError:
                continue

            if not self._within_radius_constraints(
                estimate=estimate,
                nurse=nurse,
                radius_km=radius_km,
            ):
                continue

            candidates.append(
                NurseMatchCandidate(
                    nurse=nurse,
                    distance_km=estimate.distance_km,
                    estimated_travel_time=estimate.estimated_travel_time,
                    specialization_match=True,
                    radius_km=radius_km,
                )
            )

        return candidates

    def _within_radius_constraints(
        self,
        *,
        estimate: RouteEstimate,
        nurse: NurseProfile,
        radius_km: int,
    ) -> bool:
        """Return whether route distance respects platform expansion and nurse travel radius."""
        return estimate.distance_km <= radius_km and estimate.distance_km <= nurse.travel_radius_km

    def _create_offer(
        self,
        *,
        care_request: CareRequest,
        candidate: NurseMatchCandidate,
        rank: int,
    ) -> RequestOffer:
        """Persist a request offer before notification dispatch."""
        return RequestOffer.objects.create(
            care_request=care_request,
            nurse=candidate.nurse,
            radius_km=candidate.radius_km,
            distance_km=Decimal(str(round(candidate.distance_km, 2))),
            estimated_travel_time=candidate.estimated_travel_time,
            specialization_match=candidate.specialization_match,
            rank=rank,
            expires_at=timezone.now() + timedelta(minutes=settings.REQUEST_OFFER_EXPIRY_MINUTES),
        )

    def _notify_nurse(self, *, offer: RequestOffer, candidate: NurseMatchCandidate) -> None:
        """Persist a privacy-safe job offer notification for the nurse."""
        care_request = offer.care_request
        notification = self.notification_service.notify(
            recipient=offer.nurse.user,
            notification_type=NotificationType.JOB_ASSIGNED,
            title="New care request nearby",
            body=f"{care_request.patient.user.first_name} needs {care_request.service_type}.",
            payload={
                "care_request_id": care_request.id,
                "offer_id": offer.id,
                "service_type": care_request.service_type,
                "priority": care_request.priority,
                "distance_km": candidate.distance_km,
                "estimated_travel_time": candidate.estimated_travel_time,
                "expires_at": offer.expires_at.isoformat(),
            },
            resource="CareRequest",
            resource_id=care_request.id,
        )
        offer.notification = notification
        offer.save(update_fields=["notification", "updated_at"])

    def specialization_for_service(self, service_type: str) -> str:
        """Return the nurse specialization required for a request service type."""
        return SERVICE_SPECIALIZATION_MAP[service_type]

    def _has_specialization(self, *, nurse: NurseProfile, specialization_code: str) -> bool:
        """Return whether a nurse has the required specialization."""
        return any(
            specialization.code == specialization_code
            for specialization in nurse.specializations.all()
        )
