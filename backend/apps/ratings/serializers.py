"""Rating serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.ratings.models import Rating


class RatingCreateSerializer(serializers.Serializer):
    """Validate rating creation input."""

    care_request_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)


class RatingSerializer(serializers.ModelSerializer[Rating]):
    """Serialize rating data."""

    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    nurse_id = serializers.IntegerField(source="nurse.id", read_only=True)
    nurse_name = serializers.CharField(source="nurse.user.full_name", read_only=True)
    care_request_id = serializers.IntegerField(source="care_request.id", read_only=True)

    class Meta:
        model = Rating
        fields = (
            "id",
            "patient_id",
            "nurse_id",
            "nurse_name",
            "care_request_id",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
