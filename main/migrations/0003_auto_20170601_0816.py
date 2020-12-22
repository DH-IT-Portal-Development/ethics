# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20161013_1959'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='setting',
            options={'ordering': ['order'], 'verbose_name': 'Setting'},
        ),
        migrations.AddField(
            model_name='setting',
            name='is_local',
            field=models.BooleanField(default=False),
        ),
    ]
