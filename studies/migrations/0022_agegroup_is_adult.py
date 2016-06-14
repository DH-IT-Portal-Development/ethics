# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0021_auto_20160609_0915'),
    ]

    operations = [
        migrations.AddField(
            model_name='agegroup',
            name='is_adult',
            field=models.BooleanField(default=False),
        ),
    ]
