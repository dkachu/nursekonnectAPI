"""Visit note serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.visits.models import FollowUpSchedule, VisitNote


class VisitNoteCreateSerializer(serializers.Serializer):
    """Validate visit note creation input."""

    care_request_id = serializers.IntegerField()
    vitals = serializers.CharField(required=False, allow_blank=True)
    observations = serializers.CharField(required=False, allow_blank=True)
    medication_given = serializers.CharField(required=False, allow_blank=True)
    recommendations = serializers.CharField(required=False, allow_blank=True)
    follow_up_required = serializers.BooleanField(default=False)
    follow_up_schedule = serializers.ChoiceField(
        choices=FollowUpSchedule.choices,
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        """Require a schedule when follow-up is requested."""
        follow_up_required = bool(attrs.get("follow_up_required"))
        follow_up_schedule = attrs.get("follow_up_schedule", "")
        if follow_up_required and not follow_up_schedule:
            raise serializers.ValidationError(
                {"follow_up_schedule": "Follow-up schedule is required."}
            )
        if not follow_up_required:
            attrs["follow_up_schedule"] = ""
        return attrs


class VisitNoteUpdateSerializer(serializers.Serializer):
    """Validate visit note update input."""

    vitals = serializers.CharField(required=False, allow_blank=True)
    observations = serializers.CharField(required=False, allow_blank=True)
    medication_given = serializers.CharField(required=False, allow_blank=True)
    recommendations = serializers.CharField(required=False, allow_blank=True)
    follow_up_required = serializers.BooleanField(required=False)
    follow_up_schedule = serializers.ChoiceField(
        choices=FollowUpSchedule.choices,
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        """Require a schedule when follow-up is enabled by the update."""
        if attrs.get("follow_up_required") is True and not attrs.get("follow_up_schedule"):
            raise serializers.ValidationError(
                {"follow_up_schedule": "Follow-up schedule is required."}
            )
        if attrs.get("follow_up_required") is False:
            attrs["follow_up_schedule"] = ""
        return attrs


class VisitNoteSerializer(serializers.ModelSerializer[VisitNote]):
    """Serialize protected visit note data for authorized actors."""

    care_request_id = serializers.IntegerField(source="care_request.id", read_only=True)
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    nurse_id = serializers.IntegerField(source="nurse.id", read_only=True)
    nurse_name = serializers.CharField(source="nurse.user.full_name", read_only=True)

    class Meta:
        model = VisitNote
        fields = (
            "id",
            "care_request_id",
            "patient_id",
            "nurse_id",
            "nurse_name",
            "vitals",
            "observations",
            "medication_given",
            "recommendations",
            "follow_up_required",
            "follow_up_schedule",
            "follow_up_due_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
