# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0006_auto_20160426_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervention',
            name='has_controls',
            field=models.BooleanField(default=False, verbose_name='Is er sprake van een controlegroep?'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='has_controls_details',
            field=models.TextField(verbose_name='Geef een beschrijving van de controleinterventie', blank=True),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='has_recording',
            field=models.BooleanField(default=False, verbose_name='Is er sprake van een voor- en een nameting?'),
        ),
    ]
