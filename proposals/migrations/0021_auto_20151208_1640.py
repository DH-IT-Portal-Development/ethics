# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0020_auto_20151124_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='date_reviewed',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='date_reviewed_supervisor',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_behavioristic',
            field=models.NullBooleanField(help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.', verbose_name='Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?'),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_medical',
            field=models.NullBooleanField(help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?'),
        ),
    ]
