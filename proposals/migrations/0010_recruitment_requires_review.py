# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0009_auto_20160112_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitment',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
    ]
