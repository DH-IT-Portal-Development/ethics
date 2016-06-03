# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0019_auto_20160531_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='has_surveys',
            field=models.NullBooleanField(verbose_name='Worden er vragenlijsten afgenomen bij <em>een ander dan de deelnemer</em>? Denk hierbij aan de ouder of voogd van een kind, de leraar van de klas, de arts van een pati\xebnt, etc.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='negativity_details',
            field=models.TextField(verbose_name='Licht uw antwoord toe.', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='stressful_details',
            field=models.TextField(verbose_name='Licht uw antwoord toe. Geef concrete voorbeelden van de relevante aspecten van uw studie (bijv. representatieve voorbeelden van mogelijk zeer kwetsende woorden of uitspraken in de taak, of van zeer confronterende vragen in een vragenlijst), zodat de commissie zich een goed beeld kan vormen.', blank=True),
        ),
    ]
