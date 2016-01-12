# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20160105_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='longitudinal',
        ),
        migrations.AlterField(
            model_name='study',
            name='age_groups',
            field=models.ManyToManyField(to='proposals.AgeGroup', verbose_name='Geef aan binnen welke leeftijdscategorie uw proefpersonen vallen, er zijn meerdere antwoorden mogelijk'),
        ),
    ]
