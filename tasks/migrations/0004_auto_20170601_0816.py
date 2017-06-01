# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20161013_1959'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registration',
            options={'ordering': ['order'], 'verbose_name': 'Vastlegging gedrag'},
        ),
        migrations.AddField(
            model_name='registration',
            name='is_local',
            field=models.BooleanField(default=False),
        ),
    ]
