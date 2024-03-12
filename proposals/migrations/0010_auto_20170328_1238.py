# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0009_proposal_pre_assessment_pdf"),
    ]

    operations = [
        migrations.AddField(
            model_name="funding",
            name="needs_name",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="proposal",
            name="funding_name",
            field=models.CharField(
                help_text="De titel die u hier opgeeft zal in de formele toestemmingsbrief gebruikt worden.",
                max_length=200,
                verbose_name="Wat is de naam van het gefinancierde project?",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="applicants",
            field=models.ManyToManyField(
                help_text="Als uw medeonderzoeker niet in de lijst voorkomt, vraag hem dan een keer in te loggen in het webportaal.",
                related_name="applicants",
                verbose_name="Uitvoerende(n) (inclusief uzelf). Uitvoerende(n) kunnen pas worden toegevoegd als ze eerst een keer zelf zijn ingelogd.",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="title",
            field=models.CharField(
                help_text="De titel die u hier opgeeft is zichtbaar voor de ETCL-leden en, wanneer de studie is goedgekeurd, ook voor alle UiL-OTS medewerkers die in het archief van deze portal kijken. De titel mag niet identiek zijn aan een vorige titel van een studie die u heeft ingediend.",
                unique=True,
                max_length=200,
                verbose_name="Wat is de titel van uw studie? Deze titel zal worden gebruikt in alle formele correspondentie.",
            ),
        ),
    ]
