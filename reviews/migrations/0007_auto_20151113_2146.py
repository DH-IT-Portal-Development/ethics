# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_decision_date_decision'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decision',
            name='go',
            field=models.NullBooleanField(default=None, verbose_name='Beslissing'),
        ),
        migrations.AlterField(
            model_name='review',
            name='go',
            field=models.NullBooleanField(default=None, verbose_name='Beslissing'),
        ),
    ]
