from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="is_read",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["recipient", "is_read", "created_at"],
                name="notificatio_recipie_0d7af0_idx",
            ),
        ),
    ]
