# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20170117_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='date_should_end',
            field=models.DateField(null=True, blank=True),
        ),
    ]
