# Generated by Django 4.2.11 on 2024-12-03 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0016_alter_observation_registrations"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="is_recording",
            field=models.BooleanField(default=False),
        ),
    ]