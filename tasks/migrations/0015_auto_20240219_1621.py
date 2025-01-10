# Generated by Django 3.2.23 on 2024-02-19 15:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0014_remove_session_tasks_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="repeats",
            field=models.PositiveBigIntegerField(
                default=1,
                help_text="Het kan zijn dat een zelfde sessie meerdere keren moet worden                     herhaald. Als dit het geval is, kun je dat hier                     aangeven. Als er variatie zit in de verschillende                     sessies van je onderzoek, maak dan een nieuwe sessie                     aan voor elke unieke sessie.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Hoe vaak wordt deze sessie uitgevoerd?",
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="repeats",
            field=models.PositiveBigIntegerField(
                default=1,
                help_text="Het kan zijn dat een zelfde taak meerdere keren moet worden                     herhaald binnen een sessie. Als dit het geval is, kun je dat hier                     aangeven. Als er variatie zit in de verschillende                     taken van deze sessie, maak dan een nieuwe taak                     aan voor elke unieke taak binnen deze sessie.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Hoe vaak wordt deze taak uitgevoerd binnen deze sessie?",
            ),
        ),
    ]
