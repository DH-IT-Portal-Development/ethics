# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0012_auto_20151006_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='supervisor_email',
            field=models.EmailField(help_text='Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=254, verbose_name='E-mailadres eindverantwoordelijke onderzoeker', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(default=False, verbose_name='Proefpersonen kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de proefpersonen het geval?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk_physical',
            field=models.NullBooleanField(default=False, verbose_name='Is de kans dat de proefpersoon fysieke schade oploopt tijdens het afnemen van de taak groter dan de kans op fysieke schade in het dagelijks leven?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk_psychological',
            field=models.NullBooleanField(default=False, verbose_name='Is de kans dat de proefpersoon psychische schade oploopt tijdens het afnemen van de taak groter dan de kans op psychische schade in het dagelijks leven?'),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_medical',
            field=models.NullBooleanField(default=False, help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?'),
        ),
    ]
