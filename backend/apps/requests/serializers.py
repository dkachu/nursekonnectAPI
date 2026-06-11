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
    dependent_id = serializers.SerializerMethodField()
    dependent_name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    requested_time = serializers.SerializerMethodField()
    assigned_nurse_id = serializers.SerializerMethodField()
    assigned_nurse_name = serializers.SerializerMethodField()
    accepted_at = serializers.SerializerMethodField()
    journey_started_at = serializers.SerializerMethodField()
    arrived_at = serializers.SerializerMethodField()
    visit_started_at = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    cancelled_at = serializers.SerializerMethodField()
    expired_at = serializers.SerializerMethodField()
    cancellation_reason = serializers.SerializerMethodField()

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
        """Return patient last name only to authorized actors."""
        actor = self.context.get("actor")
        if self._can_view_private_details(obj=obj, actor=actor):
            return obj.patient.user.last_name
        return ""

    def get_dependent_id(self, obj: CareRequest) -> int | None:
        """Return dependent ID only after actor has private request access."""
        if self._can_view_private_details(obj=obj, actor=self.context.get("actor")):
            return obj.dependent_id
        return None

    def get_dependent_name(self, obj: CareRequest) -> str:
        """Return dependent name only after actor has private request access."""
        if obj.dependent and self._can_view_private_details(
            obj=obj, actor=self.context.get("actor")
        ):
            return obj.dependent.full_name
        return ""

    def get_description(self, obj: CareRequest) -> str:
        """Return patient description only after acceptance or to patient/admin."""
        if self._can_view_private_details(obj=obj, actor=self.context.get("actor")):
            return obj.description
        return ""

    def get_requested_time(self, obj: CareRequest) -> object | None:
        """Return requested time only to actors with private request access."""
        if self._can_view_private_details(obj=obj, actor=self.context.get("actor")):
            return obj.requested_time
        return None

    def get_assigned_nurse_id(self, obj: CareRequest) -> int | None:
        """Return assigned nurse profile ID when the request is assigned."""
        if obj.assigned_nurse is None:
            return None
        return obj.assigned_nurse.id

    def get_assigned_nurse_name(self, obj: CareRequest) -> str:
        """Return assigned nurse display name when present."""
        if obj.assigned_nurse is None:
            return ""
        return obj.assigned_nurse.user.full_name

    def get_accepted_at(self, obj: CareRequest) -> object | None:
        """Return accepted timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "accepted_at")

    def get_journey_started_at(self, obj: CareRequest) -> object | None:
        """Return journey timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "journey_started_at")

    def get_arrived_at(self, obj: CareRequest) -> object | None:
        """Return arrival timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "arrived_at")

    def get_visit_started_at(self, obj: CareRequest) -> object | None:
        """Return visit timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "visit_started_at")

    def get_completed_at(self, obj: CareRequest) -> object | None:
        """Return completion timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "completed_at")

    def get_cancelled_at(self, obj: CareRequest) -> object | None:
        """Return cancellation timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "cancelled_at")

    def get_expired_at(self, obj: CareRequest) -> object | None:
        """Return expiry timestamp only to actors with private request access."""
        return self._private_timestamp(obj, "expired_at")

    def get_cancellation_reason(self, obj: CareRequest) -> str:
        """Return cancellation reason only to actors with private request access."""
        if self._can_view_private_details(obj=obj, actor=self.context.get("actor")):
            return obj.cancellation_reason
        return ""

    def _private_timestamp(self, obj: CareRequest, field_name: str) -> object | None:
        """Return a timestamp only to actors with private request access."""
        if self._can_view_private_details(obj=obj, actor=self.context.get("actor")):
            return getattr(obj, field_name)
        return None

    def _can_view_private_details(self, *, obj: CareRequest, actor: object | None) -> bool:
        """Return whether actor may view private care request fields."""
        if actor is None:
            return False
        if obj.patient.user_id == getattr(actor, "id", None):
            return True
        if getattr(actor, "role", None) == "ADMIN" and getattr(actor, "is_staff", False):
            return True
        return bool(obj.assigned_nurse_id and obj.assigned_nurse.user_id == actor.id)
