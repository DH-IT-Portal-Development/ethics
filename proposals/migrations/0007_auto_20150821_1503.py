# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0006_auto_20150821_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='sessions_stressful_details',
            field=models.TextField(verbose_name=b'Waarom denkt u dat?', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='session',
            name='stressful_details',
            field=models.TextField(verbose_name=b'Waarom denkt u dat?', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='session',
            name='tasks_stressful_details',
            field=models.TextField(verbose_name=b'Waarom denkt u dat?', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='stressful_details',
            field=models.TextField(verbose_name=b'Waarom denkt u dat?', blank=True),
            preserve_default=True,
        ),
    ]
