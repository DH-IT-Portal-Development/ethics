# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0009_wmo_metc_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wmo',
            name='is_behavioristic',
            field=models.PositiveIntegerField(default=1, help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken.', verbose_name='Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?', choices=[(1, 'ja'), (2, 'nee'), (3, 'twijfel')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_medical',
            field=models.PositiveIntegerField(default=1, help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?', choices=[(1, 'ja'), (2, 'nee'), (3, 'twijfel')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc',
            field=models.PositiveIntegerField(default=1, verbose_name='Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?', choices=[(1, 'ja'), (2, 'nee'), (3, 'twijfel')]),
            preserve_default=False,
        ),
    ]
