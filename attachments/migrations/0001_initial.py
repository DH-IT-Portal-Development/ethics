# Generated by Django 4.2.11 on 2024-09-23 17:00

import cdh.files.db.fields
from django.db import migrations, models
import django.db.models.deletion
import main.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("proposals", "0053_auto_20240201_1557"),
        ("files", "0004_auto_20210921_1014"),
        ("studies", "0028_remove_study_sessions_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("dmp", "Data Management Plan"),
                            ("other", "Overige bestanden"),
                            ("information_letter", "Informatiebrief"),
                            ("consent_form", "Toestemmingsverklaring"),
                        ],
                        default=("", "Gelieve selecteren"),
                        max_length=100,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default="",
                        help_text="Geef je bestand een omschrijvende naam, het liefst maar enkele woorden.",
                        max_length=50,
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        default="",
                        help_text="Geef hier je motivatie om dit bestand toe te voegen en waar je het voor gaat gebruiken tijdens je onderzoek. Eventuele opmerkingen voor de FETC kun je hier ook kwijt.",
                        max_length=2000,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="attachments.attachment",
                    ),
                ),
                (
                    "upload",
                    cdh.files.db.fields.FileField(
                        filename_generator=cdh.files.db.fields._default_filename_generator,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="files.file",
                    ),
                ),
            ],
            bases=(models.Model, main.utils.renderable),
        ),
        migrations.CreateModel(
            name="StudyAttachment",
            fields=[
                (
                    "attachment_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="attachments.attachment",
                    ),
                ),
                (
                    "attached_to",
                    models.ManyToManyField(
                        related_name="attachments", to="studies.study"
                    ),
                ),
            ],
            bases=("attachments.attachment",),
        ),
        migrations.CreateModel(
            name="ProposalAttachment",
            fields=[
                (
                    "attachment_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="attachments.attachment",
                    ),
                ),
                (
                    "attached_to",
                    models.ManyToManyField(
                        related_name="attachments", to="proposals.proposal"
                    ),
                ),
            ],
            bases=("attachments.attachment",),
        ),
    ]
