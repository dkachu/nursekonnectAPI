"""Tracking and location serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.tracking.models import TrackingLocation
from apps.tracking.services.location_updates import GPS_SOURCE, LocationFreshnessService


class LocationUpdateSerializer(serializers.Serializer):
    """Validate browser/mobile GPS location updates."""

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    source = serializers.ChoiceField(choices=[GPS_SOURCE], default=GPS_SOURCE)
    accuracy_meters = serializers.IntegerField(required=False, min_value=0, max_value=10000)


class LocationUpdateResponseSerializer(serializers.Serializer):
    """Serialize current location update results without exposing raw coordinates broadly."""

    id = serializers.IntegerField()
    role = serializers.SerializerMethodField()
    last_location_update = serializers.DateTimeField()
    location_stale = serializers.SerializerMethodField()

    def get_role(self, obj: object) -> str:
        """Return the profile owner's role."""
        return getattr(getattr(obj, "user", None), "role", "")

    def get_location_stale(self, obj: object) -> bool:
        """Return whether the location is stale after update."""
        return LocationFreshnessService().is_stale(getattr(obj, "last_location_update", None))


class TrackingLocationSerializer(serializers.ModelSerializer[TrackingLocation]):
    """Serialize nurse tracking location records."""

    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    location_stale = serializers.SerializerMethodField()
    care_request_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = TrackingLocation
        fields = (
            "id",
            "care_request_id",
            "latitude",
            "longitude",
            "recorded_at",
            "accuracy_meters",
            "location_stale",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_latitude(self, obj: TrackingLocation) -> float:
        """Return latitude from the PostGIS point."""
        return obj.location.y

    def get_longitude(self, obj: TrackingLocation) -> float:
        """Return longitude from the PostGIS point."""
        return obj.location.x

    def get_location_stale(self, obj: TrackingLocation) -> bool:
        """Return whether the tracking point is stale."""
        return LocationFreshnessService().is_stale(obj.recorded_at)
