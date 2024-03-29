# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-08 09:29
from __future__ import unicode_literals

import main.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("observations", "0003_observation_leader_has_coc"),
    ]

    operations = [
        migrations.AlterField(
            model_name="observation",
            name="approval_document",
            field=models.FileField(
                blank=True,
                upload_to="",
                validators=[main.validators.validate_pdf_or_doc],
                verbose_name="Upload hier het toestemmingsdocument (in .pdf of .doc(x)-formaat)",
            ),
        ),
    ]
