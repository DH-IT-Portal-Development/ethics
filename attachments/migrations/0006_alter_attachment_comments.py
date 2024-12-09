# Generated by Django 4.2.11 on 2024-12-05 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attachments", "0005_alter_attachment_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="comments",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Geef hier optioneel je motivatie om dit bestand toe te voegen en waar je het voor gaat gebruiken tijdens je onderzoek. Eventuele opmerkingen voor de FETC kun je hier ook kwijt.",
                max_length=2000,
            ),
        ),
    ]
