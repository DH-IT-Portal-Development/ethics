# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0013_auto_20160520_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='title',
            field=models.CharField(help_text='De titel die u hier opgeeft is zichtbaar voor de ETCL-leden en, wanneer de studie is goedgekeurd, ook voor alle UiL-OTS medewerkers die in het archief van deze portal kijken. De titel mag niet identiek zijn aan een vorige titel van een studie die u heeft ingediend.', unique=True, max_length=200, verbose_name='Wat is de titel van uw studie?'),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_behavioristic',
            field=models.CharField(blank=True, help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken. Bij observatieonderzoek waarbij er niets van de deelnemers gevraagd wordt, deze dus uitsluitend geobserveerd worden in hun leven zoals het ook had plaatsgevonden zonder de observatie, slechts dan kan "nee" ingevuld worden.', max_length=1, verbose_name='Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
    ]
