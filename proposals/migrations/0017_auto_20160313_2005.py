# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0016_auto_20160313_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervention',
            name='study',
            field=models.OneToOneField(to='proposals.Study'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='study',
            field=models.OneToOneField(to='proposals.Study'),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_intervention',
            field=models.BooleanField(default=False, verbose_name='Interventieonderzoek'),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_observation',
            field=models.BooleanField(default=False, verbose_name='Observatieonderzoek'),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_sessions',
            field=models.BooleanField(default=False, verbose_name='Taakonderzoek'),
        ),
    ]
