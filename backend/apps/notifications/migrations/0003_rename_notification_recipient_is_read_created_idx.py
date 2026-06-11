from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_notification_is_read"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="notification",
            new_name="notificatio_recipie_86ea8b_idx",
            old_name="notificatio_recipie_0d7af0_idx",
        ),
    ]
