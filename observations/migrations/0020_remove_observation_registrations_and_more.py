# Generated by Django 4.2.17 on 2025-03-26 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0019_alter_observation_details_frequency_and_more"),
        ("studies", "0036_translate_old_registrations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="observation",
            name="registrations",
        ),
        migrations.RemoveField(
            model_name="observation",
            name="registrations_details",
        ),
        migrations.DeleteModel(
            name="Registration",
        ),
    ]
