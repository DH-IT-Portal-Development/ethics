# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-14 11:50
from __future__ import unicode_literals

import main.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0014_auto_20180808_1129"),
        ("studies", "0009_agegroup_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="Documents",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "informed_consent",
                    models.FileField(
                        blank=True,
                        upload_to="",
                        validators=[main.validators.validate_pdf_or_doc],
                        verbose_name="Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)",
                    ),
                ),
                (
                    "briefing",
                    models.FileField(
                        blank=True,
                        upload_to="",
                        validators=[main.validators.validate_pdf_or_doc],
                        verbose_name="Upload hier de informatiebrief (in .pdf of .doc(x)-formaat)",
                    ),
                ),
                (
                    "director_consent_declaration",
                    models.FileField(
                        blank=True,
                        help_text="If it is already signed, upload the signed declaration form. If it is not signed yet, you can upload the unsigned document and send the document when it is signed to the secretary of the EtCL",
                        upload_to="",
                        validators=[main.validators.validate_pdf_or_doc],
                        verbose_name="Upload hier de toestemmingsverklaring van de schoolleider/hoofd van het departement (in .pdf of .doc(x)-format)",
                    ),
                ),
                (
                    "director_consent_information",
                    models.FileField(
                        blank=True,
                        upload_to="",
                        validators=[main.validators.validate_pdf_or_doc],
                        verbose_name="Upload hier de informatiebrief voor de schoolleider/hoofd van het departement (in .pdf of .doc(x)-formaat)",
                    ),
                ),
                (
                    "parents_information",
                    models.FileField(
                        blank=True,
                        upload_to="",
                        validators=[main.validators.validate_pdf_or_doc],
                        verbose_name="Upload hier de informatiebrief voor de ouders (in .pdf of .doc(x)-formaat)",
                    ),
                ),
                (
                    "proposal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="proposals.Proposal",
                    ),
                ),
                (
                    "study",
                    models.OneToOneField(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studies.Study",
                        null=True,
                    ),
                ),
            ],
        ),
    ]
