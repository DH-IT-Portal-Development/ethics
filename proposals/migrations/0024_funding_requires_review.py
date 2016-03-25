# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0023_auto_20160325_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='funding',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
    ]
