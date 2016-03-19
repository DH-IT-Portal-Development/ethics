# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0021_auto_20160319_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='observation',
        ),
        migrations.RemoveField(
            model_name='observation',
            name='study',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
        migrations.DeleteModel(
            name='Observation',
        ),
    ]
