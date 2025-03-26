# Generated by Django 4.2.17 on 2025-03-26 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0018_alter_session_tasks_duration_alter_task_description_and_more"),
        ("studies", "0036_translate_old_registrations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="registrationkind",
            name="registration",
        ),
        migrations.RemoveField(
            model_name="task",
            name="registration_kinds",
        ),
        migrations.RemoveField(
            model_name="task",
            name="registration_kinds_details",
        ),
        migrations.RemoveField(
            model_name="task",
            name="registrations",
        ),
        migrations.RemoveField(
            model_name="task",
            name="registrations_details",
        ),
        migrations.DeleteModel(
            name="Registration",
        ),
        migrations.DeleteModel(
            name="RegistrationKind",
        ),
    ]
