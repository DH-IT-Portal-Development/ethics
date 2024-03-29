# Generated by Django 2.2.18 on 2021-03-01 15:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0008_auto_20200428_1337"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="tasks_number",
            field=models.PositiveIntegerField(
                help_text='Wanneer u bijvoorbeeld eerst de deelnemer observeert en de deelnemer vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Hoeveel taken worden er binnen deze sessie bij de deelnemer afgenomen?",
            ),
        ),
    ]
