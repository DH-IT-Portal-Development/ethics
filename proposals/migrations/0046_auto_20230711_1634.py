# Generated by Django 3.2.18 on 2023-07-11 14:34

from django.db import migrations, models
import main.validators


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0045_alter_proposal_self_assessment"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="translated_forms",
            field=models.BooleanField(
                blank=True,
                default=None,
                null=True,
                verbose_name="Worden de informed consent formulieren nog vertaald naar een andere taal dan Nederlands of Engels?",
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="translated_forms_languages",
            field=models.CharField(
                blank=True,
                default=None,
                max_length=255,
                null=True,
                verbose_name="Andere talen:",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="comments",
            field=models.TextField(
                blank=True,
                validators=[main.validators.MaxWordsValidator(1000)],
                verbose_name="Ruimte voor eventuele opmerkingen. Gebruik maximaal 1000 woorden.",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="self_assessment",
            field=models.TextField(
                blank=True,
                validators=[main.validators.MaxWordsValidator(1000)],
                verbose_name="Wat zijn de belangrijkste ethische kwesties in dit onderzoek en beschrijf kort hoe ga je daarmee omgaat.  Gebruik maximaal 1000 woorden.",
            ),
        ),
    ]
