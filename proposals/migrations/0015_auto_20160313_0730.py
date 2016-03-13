# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0014_auto_20160313_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='date_end',
            field=models.DateField(null=True, verbose_name='Wat is de beoogde einddatum van uw studie (indien bekend)?', blank=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='summary',
            field=models.TextField(verbose_name='Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.'),
        ),
    ]
