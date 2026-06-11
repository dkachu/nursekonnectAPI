"""Nurse-domain serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.nurses.models import (
    NurseAvailabilitySlot,
    NurseCredential,
    NurseProfile,
    NurseSpecialization,
    NurseSpecializationCode,
    NurseVerificationStatus,
)
from apps.nurses.services.discovery import NearbyNurseResult


class NurseSpecializationSerializer(serializers.ModelSerializer[NurseSpecialization]):
    """Serialize supported nurse specializations."""

    class Meta:
        model = NurseSpecialization
        fields = ("id", "code", "name")
        read_only_fields = fields


class NurseProfileSerializer(serializers.ModelSerializer[NurseProfile]):
    """Serialize nurse profile data."""

    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email_verified = serializers.BooleanField(source="user.email_verified", read_only=True)
    phone_verified = serializers.BooleanField(source="user.phone_verified", read_only=True)
    specializations = NurseSpecializationSerializer(many=True, read_only=True)

    class Meta:
        model = NurseProfile
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "email_verified",
            "phone_verified",
            "national_id",
            "gender",
            "date_of_birth",
            "profile_photo",
            "nck_license_number",
            "nck_license_expiry",
            "nck_verification_status",
            "specializations",
            "years_of_experience",
            "bio",
            "county",
            "address",
            "last_location_update",
            "location_visible",
            "status",
            "is_available",
            "travel_radius_km",
            "rating",
            "reputation_score",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "email_verified",
            "phone_verified",
            "nck_verification_status",
            "last_location_update",
            "status",
            "is_available",
            "rating",
            "reputation_score",
            "created_at",
            "updated_at",
        )


class NurseSpecializationUpdateSerializer(serializers.Serializer):
    """Validate specialization code updates."""

    specializations = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


class NurseStatusSerializer(serializers.Serializer):
    """Validate nurse status updates."""

    status = serializers.ChoiceField(choices=NurseProfile._meta.get_field("status").choices)
    location_visible = serializers.BooleanField(required=False)


class NurseVerificationSerializer(serializers.ModelSerializer[NurseProfile]):
    """Validate administrator NCK verification updates."""

    class Meta:
        model = NurseProfile
        fields = (
            "nck_license_number",
            "nck_license_expiry",
            "nck_verification_status",
        )


class NurseCredentialSerializer(serializers.ModelSerializer[NurseCredential]):
    """Serialize nurse credential images."""

    class Meta:
        model = NurseCredential
        fields = (
            "id",
            "credential_type",
            "image",
            "verification_status",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "verification_status",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        )


class NurseCredentialReviewSerializer(serializers.ModelSerializer[NurseCredential]):
    """Validate credential review decisions."""

    class Meta:
        model = NurseCredential
        fields = ("verification_status", "review_notes")

    def validate_verification_status(self, value: str) -> str:
        """Restrict credential review terminal states."""
        if value not in {
            NurseVerificationStatus.UNDER_REVIEW,
            NurseVerificationStatus.VERIFIED,
            NurseVerificationStatus.REJECTED,
            NurseVerificationStatus.EXPIRED,
        }:
            raise serializers.ValidationError("Unsupported review status.")
        return value


class NurseAvailabilitySlotSerializer(serializers.ModelSerializer[NurseAvailabilitySlot]):
    """Serialize nurse availability slots."""

    class Meta:
        model = NurseAvailabilitySlot
        fields = ("id", "day_of_week", "start_time", "end_time", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        """Ensure availability windows move forward in time."""
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("start_time must be before end_time.")
        return attrs


class NearbyNurseQuerySerializer(serializers.Serializer):
    """Validate nearby nurse discovery filters."""

    specialization = serializers.ChoiceField(
        choices=NurseSpecializationCode.choices,
        required=False,
    )
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=20)


class NearbyNurseResultSerializer(serializers.Serializer):
    """Serialize privacy-safe nearby nurse discovery results."""

    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    years_of_experience = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    reputation_score = serializers.SerializerMethodField()
    average_response_seconds = serializers.SerializerMethodField()
    specializations = serializers.SerializerMethodField()
    specialization_match = serializers.BooleanField()
    distance_km = serializers.FloatField()
    estimated_travel_time = serializers.IntegerField()

    def get_id(self, obj: NearbyNurseResult) -> int:
        """Return the nurse profile identifier."""
        return obj.nurse.id

    def get_first_name(self, obj: NearbyNurseResult) -> str:
        """Return the nurse user's first name."""
        return obj.nurse.user.first_name

    def get_last_name(self, obj: NearbyNurseResult) -> str:
        """Return the nurse user's last name."""
        return obj.nurse.user.last_name

    def get_profile_photo(self, obj: NearbyNurseResult) -> str:
        """Return the profile photo URL or an empty string."""
        return obj.nurse.profile_photo.url if obj.nurse.profile_photo else ""

    def get_years_of_experience(self, obj: NearbyNurseResult) -> int:
        """Return the nurse's years of experience."""
        return obj.nurse.years_of_experience

    def get_rating(self, obj: NearbyNurseResult) -> str:
        """Return the nurse's public rating."""
        return str(obj.nurse.rating)

    def get_reputation_score(self, obj: NearbyNurseResult) -> str:
        """Return the nurse's reputation score."""
        return str(obj.nurse.reputation_score)

    def get_average_response_seconds(self, obj: NearbyNurseResult) -> int:
        """Return the nurse's average response speed signal."""
        return obj.nurse.average_response_seconds

    def get_specializations(self, obj: NearbyNurseResult) -> list[dict[str, str]]:
        """Return prefetched specialization summaries."""
        return [
            {"code": specialization.code, "name": specialization.name}
            for specialization in obj.nurse.specializations.all()
        ]
