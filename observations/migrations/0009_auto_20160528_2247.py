# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0008_auto_20160520_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='days',
            field=models.PositiveIntegerField(verbose_name='Op hoeveel dagen wordt er geobserveerd (per deelnemer)?'),
        ),
    ]
