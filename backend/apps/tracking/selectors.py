"""Optimized geospatial selectors."""

from __future__ import annotations

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import QuerySet

from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.tracking.models import TrackingLocation
from apps.tracking.services.location_updates import LocationFreshnessService


class LocationSelector:
    """Read location-backed resources with freshness constraints."""

    def fresh_nurses(self) -> QuerySet[NurseProfile]:
        """Return nurses with fresh visible locations that can participate in matching."""
        return (
            NurseProfile.objects.select_related("user")
            .prefetch_related("specializations")
            .filter(
                current_location__isnull=False,
                last_location_update__gte=LocationFreshnessService().stale_cutoff(),
                status=NurseStatus.ONLINE,
                is_available=True,
                location_visible=True,
                nck_verification_status=NurseVerificationStatus.VERIFIED,
            )
        )

    def candidate_nurses_within_radius(
        self,
        *,
        origin: Point,
        radius_km: int,
    ) -> QuerySet[NurseProfile]:
        """Return fresh nurse candidates inside a PostGIS radius prefilter."""
        return (
            self.fresh_nurses()
            .filter(current_location__distance_lte=(origin, D(km=radius_km)))
            .annotate(distance_m=Distance("current_location", origin))
            .order_by("distance_m", "-reputation_score")
        )


class TrackingLocationSelector:
    """Read nurse tracking history."""

    def recent_for_nurse(
        self,
        nurse: NurseProfile,
        *,
        limit: int = 20,
    ) -> QuerySet[TrackingLocation]:
        """Return recent tracking points for a nurse."""
        return nurse.tracking_locations.all()[:limit]
