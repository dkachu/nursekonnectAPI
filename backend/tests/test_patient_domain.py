"""Patient-domain tests."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.audit_logs.models import MedicalAccessLog
from apps.patients.models import EmergencyContact, Gender, PatientDependent, PatientProfile
from apps.patients.services.access import PatientMedicalAccessService

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def authenticate(client: APIClient, user: object) -> None:
    """Authenticate a client with a JWT access token."""
    tokens = TokenService().issue_pair(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access}")


@pytest.fixture
def patient_user() -> object:
    """Create a patient user and profile."""
    user = User.objects.create_user(
        email="patient-domain@example.com",
        password="StrongPassword123!",
        first_name="Patient",
        last_name="Domain",
        role=UserRole.PATIENT,
    )
    PatientProfile.objects.create(user=user, phone_number="+254700000010")
    return user


@pytest.fixture
def other_patient_user() -> object:
    """Create another patient user and profile."""
    user = User.objects.create_user(
        email="other-patient@example.com",
        password="StrongPassword123!",
        first_name="Other",
        last_name="Patient",
        role=UserRole.PATIENT,
    )
    PatientProfile.objects.create(user=user, phone_number="+254700000011")
    return user


@pytest.fixture
def nurse_user() -> object:
    """Create a nurse user."""
    return User.objects.create_user(
        email="patient-domain-nurse@example.com",
        password="StrongPassword123!",
        first_name="Nurse",
        last_name="Domain",
        role=UserRole.NURSE,
    )


@pytest.fixture
def admin_user() -> object:
    """Create an authorized admin user."""
    return User.objects.create_superuser(
        email="patient-domain-admin@example.com",
        password="StrongPassword123!",
        first_name="Admin",
        last_name="Domain",
    )


@pytest.mark.django_db
def test_patient_can_patch_and_read_profile_with_medical_access_log(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """Patient can update own profile and reads create access logs."""
    authenticate(api_client, patient_user)

    patch_response = api_client.patch(
        reverse("patient-profile"),
        {
            "national_id": "12345678",
            "gender": Gender.FEMALE,
            "date_of_birth": "1990-01-01",
            "blood_group": "O+",
            "allergies": "Penicillin",
            "chronic_conditions": "Asthma",
            "current_medications": "Salbutamol",
            "medical_notes": "Prefers morning visits",
            "county": "Nairobi",
            "address": "Westlands",
        },
        format="json",
    )

    assert patch_response.status_code == 200
    assert patch_response.data["allergies"] == "Penicillin"

    get_response = api_client.get(reverse("patient-profile"))

    assert get_response.status_code == 200
    assert get_response.data["medical_notes"] == "Prefers morning visits"
    assert MedicalAccessLog.objects.filter(
        actor=patient_user,
        patient=patient_user.patient_profile,
        resource="PatientProfile.medical_information",
    ).exists()


@pytest.mark.django_db
def test_medical_fields_are_encrypted_at_rest(patient_user: object) -> None:
    """Protected medical fields are not stored as plaintext."""
    profile = patient_user.patient_profile
    profile.allergies = "Latex"
    profile.chronic_conditions = "Diabetes"
    profile.current_medications = "Metformin"
    profile.medical_notes = "Sensitive note"
    profile.save()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT allergies, chronic_conditions, current_medications, medical_notes
            FROM patients_patientprofile
            WHERE id = %s
            """,
            [profile.id],
        )
        stored_values = cursor.fetchone()

    assert all(value.startswith("enc$") for value in stored_values)
    assert "Latex" not in " ".join(stored_values)
    profile.refresh_from_db()
    assert profile.allergies == "Latex"
    assert profile.medical_notes == "Sensitive note"


@pytest.mark.django_db
def test_patient_can_manage_emergency_contacts(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """Patient can create, list, update, and delete own emergency contacts."""
    authenticate(api_client, patient_user)

    create_response = api_client.post(
        reverse("patient-emergency-contact-list"),
        {"name": "Mary Doe", "phone_number": "+254700000012", "relationship": "Spouse"},
        format="json",
    )
    contact_id = create_response.data["id"]
    list_response = api_client.get(reverse("patient-emergency-contact-list"))
    update_response = api_client.patch(
        reverse("patient-emergency-contact-detail", kwargs={"contact_id": contact_id}),
        {"relationship": "Parent"},
        format="json",
    )
    delete_response = api_client.delete(
        reverse("patient-emergency-contact-detail", kwargs={"contact_id": contact_id})
    )

    assert create_response.status_code == 201
    assert len(list_response.data) == 1
    assert update_response.data["relationship"] == "Parent"
    assert delete_response.status_code == 204
    assert EmergencyContact.objects.count() == 0


@pytest.mark.django_db
def test_patient_can_manage_dependents(api_client: APIClient, patient_user: object) -> None:
    """Patient can create, list, update, and delete own dependents."""
    authenticate(api_client, patient_user)

    create_response = api_client.post(
        reverse("patient-dependent-list"),
        {
            "full_name": "Child Doe",
            "date_of_birth": "2018-01-01",
            "gender": Gender.MALE,
            "relationship": "Child",
            "medical_notes": "Mild eczema",
        },
        format="json",
    )
    dependent_id = create_response.data["id"]
    list_response = api_client.get(reverse("patient-dependent-list"))
    update_response = api_client.patch(
        reverse("patient-dependent-detail", kwargs={"dependent_id": dependent_id}),
        {"medical_notes": "No current issues"},
        format="json",
    )
    delete_response = api_client.delete(
        reverse("patient-dependent-detail", kwargs={"dependent_id": dependent_id})
    )

    assert create_response.status_code == 201
    assert list_response.data[0]["medical_notes"] == "Mild eczema"
    assert update_response.data["medical_notes"] == "No current issues"
    assert delete_response.status_code == 204
    assert PatientDependent.objects.count() == 0


@pytest.mark.django_db
def test_dependent_medical_notes_are_encrypted(patient_user: object) -> None:
    """Dependent medical notes are encrypted at rest."""
    dependent = PatientDependent.objects.create(
        patient=patient_user.patient_profile,
        full_name="Encrypted Child",
        date_of_birth="2018-01-01",
        gender=Gender.FEMALE,
        relationship="Child",
        medical_notes="Sensitive dependent note",
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT medical_notes FROM patients_patientdependent WHERE id = %s",
            [dependent.id],
        )
        stored_note = cursor.fetchone()[0]

    assert stored_note.startswith("enc$")
    assert "Sensitive dependent note" not in stored_note
    dependent.refresh_from_db()
    assert dependent.medical_notes == "Sensitive dependent note"


@pytest.mark.django_db
def test_other_patient_and_nurse_cannot_access_medical_information(
    api_client: APIClient,
    patient_user: object,
    other_patient_user: object,
    nurse_user: object,
) -> None:
    """Only the patient, assigned nurse, or authorized admin can read medical data."""
    target_patient_id = patient_user.patient_profile.id

    authenticate(api_client, other_patient_user)
    other_response = api_client.get(
        reverse("patient-medical-information", kwargs={"patient_id": target_patient_id})
    )

    authenticate(api_client, nurse_user)
    nurse_response = api_client.get(
        reverse("patient-medical-information", kwargs={"patient_id": target_patient_id})
    )

    assert other_response.status_code == 403
    assert nurse_response.status_code == 403
    assert MedicalAccessLog.objects.count() == 0


@pytest.mark.django_db
def test_patient_and_authorized_admin_can_access_medical_information(
    api_client: APIClient,
    patient_user: object,
    admin_user: object,
) -> None:
    """Patient and authorized admin can read protected data and create logs."""
    profile = patient_user.patient_profile
    profile.allergies = "Peanuts"
    profile.save()

    authenticate(api_client, patient_user)
    patient_response = api_client.get(
        reverse("patient-medical-information", kwargs={"patient_id": profile.id})
    )

    authenticate(api_client, admin_user)
    admin_response = api_client.get(
        reverse("patient-medical-information", kwargs={"patient_id": profile.id})
    )

    assert patient_response.status_code == 200
    assert patient_response.data["allergies"] == "Peanuts"
    assert admin_response.status_code == 200
    assert MedicalAccessLog.objects.filter(patient=profile).count() == 2


@pytest.mark.django_db
def test_non_staff_admin_is_not_authorized_for_medical_information(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """Admin role without staff authorization cannot read protected data."""
    non_staff_admin = User.objects.create_user(
        email="nonstaff-admin@example.com",
        password="StrongPassword123!",
        first_name="Nonstaff",
        last_name="Admin",
        role=UserRole.ADMIN,
        is_staff=False,
    )
    authenticate(api_client, non_staff_admin)

    response = api_client.get(
        reverse(
            "patient-medical-information",
            kwargs={"patient_id": patient_user.patient_profile.id},
        )
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_nurse_assignment_access_denies_by_default(
    nurse_user: object,
    patient_user: object,
) -> None:
    """Assigned-nurse access is denied until care request assignment exists."""
    assert (
        PatientMedicalAccessService().can_access_medical_data(
            actor=nurse_user,
            patient=patient_user.patient_profile,
        )
        is False
    )


@pytest.mark.django_db
def test_patient_endpoints_reject_non_patients(
    api_client: APIClient,
    nurse_user: object,
) -> None:
    """Nurses cannot use patient-owned management endpoints."""
    authenticate(api_client, nurse_user)

    profile_response = api_client.get(reverse("patient-profile"))
    contacts_response = api_client.get(reverse("patient-emergency-contact-list"))
    dependents_response = api_client.get(reverse("patient-dependent-list"))

    assert profile_response.status_code == 403
    assert contacts_response.status_code == 403
    assert dependents_response.status_code == 403
