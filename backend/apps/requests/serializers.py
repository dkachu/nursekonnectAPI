"""Care request serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.requests.models import CareRequest, CareRequestPriority, CareServiceType


class CareRequestCreateSerializer(serializers.Serializer):
    """Validate care request creation input."""

    dependent_id = serializers.IntegerField(required=False, allow_null=True)
    service_type = serializers.ChoiceField(choices=CareServiceType.choices)
    priority = serializers.ChoiceField(
        choices=CareRequestPriority.choices,
        default=CareRequestPriority.NORMAL,
    )
    description = serializers.CharField(required=False, allow_blank=True)
    requested_time = serializers.DateTimeField(required=False)


class CareRequestCancelSerializer(serializers.Serializer):
    """Validate cancellation payloads."""

    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class CareRequestSerializer(serializers.ModelSerializer[CareRequest]):
    """Serialize care requests without exposing protected medical details."""

    patient_first_name = serializers.CharField(source="patient.user.first_name", read_only=True)
    patient_last_name = serializers.SerializerMethodField()
    dependent_id = serializers.IntegerField(source="dependent.id", read_only=True)
    dependent_name = serializers.CharField(source="dependent.full_name", read_only=True)
    assigned_nurse_id = serializers.IntegerField(source="assigned_nurse.id", read_only=True)
    assigned_nurse_name = serializers.SerializerMethodField()

    class Meta:
        model = CareRequest
        fields = (
            "id",
            "patient_first_name",
            "patient_last_name",
            "dependent_id",
            "dependent_name",
            "service_type",
            "priority",
            "description",
            "requested_time",
            "status",
            "assigned_nurse_id",
            "assigned_nurse_name",
            "accepted_at",
            "journey_started_at",
            "arrived_at",
            "visit_started_at",
            "completed_at",
            "cancelled_at",
            "expired_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_patient_last_name(self, obj: CareRequest) -> str:
        """Return patient last name only to the patient owner and administrators."""
        actor = self.context.get("actor")
        if actor and (obj.patient.user_id == actor.id or getattr(actor, "is_staff", False)):
            return obj.patient.user.last_name
        return ""

    def get_assigned_nurse_name(self, obj: CareRequest) -> str:
        """Return assigned nurse display name when present."""
        if obj.assigned_nurse is None:
            return ""
        return obj.assigned_nurse.user.full_name
