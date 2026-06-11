"""Nurse-domain serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.nurses.models import (
    NurseAvailabilitySlot,
    NurseCredential,
    NurseProfile,
    NurseSpecialization,
    NurseVerificationStatus,
)


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
