"""Patient-domain serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.patients.models import EmergencyContact, PatientDependent, PatientProfile


class PatientProfileSerializer(serializers.ModelSerializer[PatientProfile]):
    """Serialize patient profile data for the owner."""

    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email_verified = serializers.BooleanField(source="user.email_verified", read_only=True)
    phone_verified = serializers.BooleanField(source="user.phone_verified", read_only=True)

    class Meta:
        model = PatientProfile
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "phone_verified",
            "email_verified",
            "national_id",
            "gender",
            "date_of_birth",
            "profile_photo",
            "blood_group",
            "allergies",
            "chronic_conditions",
            "current_medications",
            "disabilities",
            "medical_notes",
            "county",
            "address",
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
            "created_at",
            "updated_at",
        )


class PatientMedicalInformationSerializer(serializers.ModelSerializer[PatientProfile]):
    """Serialize protected medical information."""

    class Meta:
        model = PatientProfile
        fields = (
            "id",
            "allergies",
            "chronic_conditions",
            "current_medications",
            "disabilities",
            "medical_notes",
            "blood_group",
        )
        read_only_fields = fields


class EmergencyContactSerializer(serializers.ModelSerializer[EmergencyContact]):
    """Serialize emergency contacts."""

    class Meta:
        model = EmergencyContact
        fields = ("id", "name", "phone_number", "relationship", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class PatientDependentSerializer(serializers.ModelSerializer[PatientDependent]):
    """Serialize patient dependents."""

    class Meta:
        model = PatientDependent
        fields = (
            "id",
            "full_name",
            "date_of_birth",
            "gender",
            "relationship",
            "medical_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
