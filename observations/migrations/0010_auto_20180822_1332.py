# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-22 11:32
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("observations", "0009_auto_20180822_1328"),
    ]

    operations = [
        migrations.AlterField(
            model_name="observation",
            name="days",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Op hoeveel dagen wordt er geobserveerd (per deelnemer)?",
            ),
        ),
        migrations.AlterField(
            model_name="observation",
            name="mean_hours",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=4,
                null=True,
                validators=[django.core.validators.MaxValueValidator(24)],
                verbose_name="Hoeveel uur wordt er gemiddeld per dag geobserveerd?",
            ),
        ),
    ]
