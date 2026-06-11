"""Journey tracking and proximity validation services."""

from __future__ import annotations

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.db.models import QuerySet
from django.utils import timezone

from apps.nurses.models import NurseProfile
from apps.requests.models import CareRequest, CareRequestStatus
from apps.tracking.models import TrackingLocation
from apps.tracking.services.location_updates import LocationFreshnessService


class JourneySelector:
    """Read active assigned journey state for nurse tracking."""

    def active_en_route_request_for_nurse(self, nurse: NurseProfile) -> CareRequest:
        """Return the nurse's active en-route care request."""
        return CareRequest.objects.select_related("patient", "patient__user", "assigned_nurse").get(
            assigned_nurse=nurse,
            status=CareRequestStatus.NURSE_EN_ROUTE,
            is_deleted=False,
        )

    def recent_tracking_for_request(
        self,
        *,
        care_request: CareRequest,
        nurse: NurseProfile,
    ) -> QuerySet[TrackingLocation]:
        """Return recent tracking points for a nurse/request pair."""
        return TrackingLocation.objects.filter(care_request=care_request, nurse=nurse).order_by(
            "-recorded_at"
        )


class JourneyTrackingService:
    """Validate journey GPS cadence and assigned request context."""

    def __init__(self, *, selector: JourneySelector | None = None) -> None:
        self.selector = selector or JourneySelector()

    def active_request_for_tracking(self, *, nurse: NurseProfile) -> CareRequest:
        """Return the active request that should receive tracking points."""
        return self.selector.active_en_route_request_for_nurse(nurse)

    def validate_tracking_cadence(
        self,
        *,
        care_request: CareRequest,
        nurse: NurseProfile,
        recorded_at,
    ) -> None:
        """Ensure nurse tracking updates are not sent more frequently than allowed."""
        latest = self.selector.recent_tracking_for_request(
            care_request=care_request,
            nurse=nurse,
        ).first()
        if latest is None:
            return

        elapsed_seconds = (recorded_at - latest.recorded_at).total_seconds()
        if elapsed_seconds < settings.TRACKING_MIN_INTERVAL_SECONDS:
            raise ValueError("Tracking updates must be at least 30 seconds apart.")


class JourneyProximityService:
    """Validate nurse proximity to patient request locations."""

    def ensure_fresh_nurse_location(self, *, nurse: NurseProfile) -> None:
        """Require a fresh GPS fix before journey actions."""
        if nurse.current_location is None:
            raise ValueError("Fresh nurse GPS location is required.")
        if LocationFreshnessService().is_stale(nurse.last_location_update):
            raise ValueError("Fresh nurse GPS location is required.")

    def distance_to_request_meters(self, *, care_request: CareRequest) -> float:
        """Return PostGIS distance from assigned nurse to request location in meters."""
        nurse = care_request.assigned_nurse
        if nurse is None or nurse.current_location is None:
            raise ValueError("Fresh nurse GPS location is required.")
        result = (
            CareRequest.objects.filter(id=care_request.id)
            .annotate(distance_to_nurse=Distance("location", nurse.current_location))
            .get()
        )
        return float(result.distance_to_nurse.m)

    def ensure_within_arrival_distance(self, *, care_request: CareRequest) -> None:
        """Require nurse to be within the configured 100m proximity rule."""
        self.ensure_fresh_nurse_location(nurse=care_request.assigned_nurse)
        distance_m = self.distance_to_request_meters(care_request=care_request)
        if distance_m > settings.ARRIVAL_VERIFICATION_DISTANCE_METERS:
            raise ValueError("Nurse must be within 100 meters of the patient location.")

    def touch_nurse_location(self, *, nurse: NurseProfile) -> None:
        """Refresh timestamp when a journey starts from an already stored GPS fix."""
        nurse.last_location_update = timezone.now()
        nurse.save(update_fields=["last_location_update", "updated_at"])
