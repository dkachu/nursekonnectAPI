from __future__ import annotations

from django.db import migrations

SPECIALIZATIONS = [
    ("GENERAL_NURSING", "General nursing"),
    ("WOUND_CARE", "Wound care"),
    ("GERIATRIC_CARE", "Geriatric care"),
    ("PALLIATIVE_CARE", "Palliative care"),
    ("PEDIATRIC_CARE", "Pediatric care"),
    ("MIDWIFERY", "Midwifery"),
    ("MENTAL_HEALTH", "Mental health"),
    ("ICU_CARE", "ICU care"),
    ("POST_SURGICAL_CARE", "Post-surgical care"),
    ("CHRONIC_DISEASE_SUPPORT", "Chronic disease support"),
]


def seed_specializations(apps: object, schema_editor: object) -> None:
    NurseSpecialization = apps.get_model("nurses", "NurseSpecialization")
    for code, name in SPECIALIZATIONS:
        NurseSpecialization.objects.update_or_create(code=code, defaults={"name": name})


class Migration(migrations.Migration):
    dependencies = [
        ("nurses", "0002_nursespecialization_nurseprofile_address_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_specializations, migrations.RunPython.noop),
    ]
