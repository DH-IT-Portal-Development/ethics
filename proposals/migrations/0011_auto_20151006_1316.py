# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0010_auto_20151006_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='comments',
            field=models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='feedback_details',
            field=models.CharField(max_length=200, verbose_name='Beschrijf hoe de feedback wordt gegeven.', blank=True),
        ),
    ]
