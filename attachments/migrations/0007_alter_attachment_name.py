# Generated by Django 4.2.11 on 2024-12-19 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attachments", "0006_alter_attachment_comments_alter_attachment_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="name",
            field=models.CharField(
                default="",
                help_text="Geef je bestand een omschrijvende naam, het liefst maar enkele woorden.",
                max_length=50,
                verbose_name="Omschrijving",
            ),
        ),
    ]