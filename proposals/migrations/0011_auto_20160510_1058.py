# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0010_auto_20160510_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wmo',
            name='is_behavioristic',
            field=models.CharField(default=None, help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken.', max_length=1, verbose_name='Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_medical',
            field=models.CharField(default=None, help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', max_length=1, verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc',
            field=models.CharField(default=None, max_length=1, verbose_name='Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')]),
        ),
    ]
