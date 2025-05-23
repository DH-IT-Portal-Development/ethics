# Generated by Django 4.2.20 on 2025-04-24 12:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0018_alter_session_tasks_duration_alter_task_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="repeats",
            field=models.PositiveBigIntegerField(
                default=1,
                help_text="Het kan zijn dat een zelfde sessie meerdere keren moet worden                     uitgevoerd. Als dit het geval is, kun je dat hier                     aangeven. Als er variatie zit in de verschillende                     sessies van je onderzoek, maak dan een nieuwe sessie                     aan voor elke unieke sessie.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Hoe vaak wordt deze sessie uitgevoerd (per deelnemer)?",
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="repeats",
            field=models.PositiveBigIntegerField(
                default=1,
                help_text="Het kan zijn dat eenzelfde taak meerdere keren moet worden                     uitgevoerd binnen een sessie. Als dit het geval is, kun je dat hier                     aangeven. Als er variatie zit in de verschillende                     taken van deze sessie, maak dan een nieuwe taak                     aan voor elke unieke taak binnen deze sessie.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Hoe vaak wordt deze taak uitgevoerd binnen deze sessie (per deelnemer)?",
            ),
        ),
    ]
