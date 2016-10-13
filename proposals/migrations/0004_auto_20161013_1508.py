# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20161008_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='funding',
            name='description_en',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='funding',
            name='description_nl',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='relation',
            name='description_en',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='relation',
            name='description_nl',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
