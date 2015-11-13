# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0018_auto_20151013_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='agegroup',
            name='max_net_duration',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='compensation',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='setting',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
    ]
