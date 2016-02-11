# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0004_auto_20160211_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='feedback_details',
            field=models.TextField(verbose_name='Beschrijf hoe de feedback wordt gegeven.', blank=True),
        ),
    ]
