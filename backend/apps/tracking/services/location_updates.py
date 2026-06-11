"""GPS location update services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.nurses.models import NurseProfile
from apps.patients.models import PatientProfile
from apps.tracking.models import TrackingLocation

GPS_SOURCE = "GPS"


@dataclass(frozen=True)
class LocationUpdateInput:
    """Validated browser/mobile GPS payload."""

    latitude: float
    longitude: float
    source: str = GPS_SOURCE
    accuracy_meters: int | None = None


class LocationUpdateService:
    """Apply GPS updates to patient and nurse profiles."""

    def point_from_input(self, data: LocationUpdateInput) -> Point:
        """Convert GPS latitude and longitude into a WGS84 point."""
        self.validate_gps_input(data)
        return Point(data.longitude, data.latitude, srid=4326)

    def validate_gps_input(self, data: LocationUpdateInput) -> None:
        """Validate that a payload came from device GPS and is geographically valid."""
        if data.source != GPS_SOURCE:
            raise ValueError("Location source must be browser/mobile GPS.")
        if not -90 <= data.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        if not -180 <= data.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

    @transaction.atomic
    def update_current_location(
        self,
        *,
        actor: object,
        data: LocationUpdateInput,
    ) -> PatientProfile | NurseProfile:
        """Update the authenticated patient's or nurse's latest GPS location."""
        point = self.point_from_input(data)
        now = timezone.now()
        role = getattr(actor, "role", None)

        if role == UserRole.PATIENT:
            patient = PatientProfile.objects.select_for_update().get(user=actor)
            patient.current_location = point
            patient.last_location_update = now
            patient.save(update_fields=["current_location", "last_location_update", "updated_at"])
            return patient

        if role == UserRole.NURSE:
            nurse = NurseProfile.objects.select_for_update().get(user=actor)
            nurse.current_location = point
            nurse.last_location_update = now
            nurse.save(update_fields=["current_location", "last_location_update", "updated_at"])
            return nurse

        raise PermissionError("Only patients and nurses can update location.")

    @transaction.atomic
    def record_tracking_location(
        self,
        *,
        actor: object,
        data: LocationUpdateInput,
    ) -> TrackingLocation:
        """Record a nurse journey GPS point and refresh the nurse's latest location."""
        if getattr(actor, "role", None) != UserRole.NURSE:
            raise PermissionError("Only nurses can submit tracking locations.")

        point = self.point_from_input(data)
        now = timezone.now()
        nurse = NurseProfile.objects.select_for_update().get(user=actor)
        from apps.tracking.services.journey import JourneyTrackingService

        journey_service = JourneyTrackingService()
        care_request = journey_service.active_request_for_tracking(nurse=nurse)
        journey_service.validate_tracking_cadence(
            care_request=care_request,
            nurse=nurse,
            recorded_at=now,
        )
        nurse.current_location = point
        nurse.last_location_update = now
        nurse.save(update_fields=["current_location", "last_location_update", "updated_at"])
        return TrackingLocation.objects.create(
            nurse=nurse,
            care_request=care_request,
            location=point,
            recorded_at=now,
            accuracy_meters=data.accuracy_meters,
        )


class LocationFreshnessService:
    """Evaluate location freshness using the configured stale window."""

    def stale_cutoff(self):
        """Return the oldest timestamp still considered fresh."""
        return timezone.now() - timedelta(minutes=settings.MAX_LOCATION_AGE_MINUTES)

    def is_stale(self, last_location_update) -> bool:
        """Return whether a location timestamp is missing or stale."""
        return not last_location_update or last_location_update < self.stale_cutoff()
