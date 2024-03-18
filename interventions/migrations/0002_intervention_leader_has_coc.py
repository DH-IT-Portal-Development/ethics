# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("interventions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="intervention",
            name="leader_has_coc",
            field=models.NullBooleanField(
                help_text='Iedereen die op een school werkt moet in het bezit         zijn van een Verklaring Omtrent Gedrag (VOG, zie         <a href="https://www.justis.nl/producten/vog/"         target="_blank">https://www.justis.nl/producten/vog/</a>).         Het is de verantwoordelijkheid van de school om hierom te vragen.         De ETCL neemt hierin een adviserende rol en wil de onderzoekers         waarschuwen dat de school om een VOG kan vragen.',
                verbose_name="Is de testleider in het bezit van een VOG?",
            ),
        ),
    ]
