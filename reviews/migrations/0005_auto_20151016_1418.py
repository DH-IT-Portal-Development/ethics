# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20151013_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decision',
            name='go',
            field=models.NullBooleanField(verbose_name='Beslissing'),
        ),
        migrations.AlterField(
            model_name='review',
            name='go',
            field=models.NullBooleanField(verbose_name='Beslissing'),
        ),
    ]
