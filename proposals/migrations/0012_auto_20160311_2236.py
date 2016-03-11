# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0011_auto_20160311_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='has_intervention',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='study',
            name='has_observation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='study',
            name='has_sessions',
            field=models.BooleanField(default=False),
        ),
    ]
