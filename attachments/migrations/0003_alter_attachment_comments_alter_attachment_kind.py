# Generated by Django 4.2.11 on 2024-11-12 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attachments", "0002_attachment_author_alter_attachment_upload"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="comments",
            field=models.TextField(
                default="",
                help_text="Geef hier optioneel je motivatie om dit bestand toe te voegen en waar je het voor gaat gebruiken tijdens je onderzoek. Eventuele opmerkingen voor de FETC kun je hier ook kwijt.",
                max_length=2000,
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="kind",
            field=models.CharField(
                default=("other", "Overig bestand"),
                max_length=100,
                verbose_name="Type bestand",
            ),
        ),
    ]
