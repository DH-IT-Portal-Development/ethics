# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0007_auto_20161219_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='relation',
            name='check_pre_assessment',
            field=models.BooleanField(default=True),
        ),
    ]
