# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20151016_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='date_decision',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
