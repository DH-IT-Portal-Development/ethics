# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0014_auto_20160528_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='status_review',
            field=models.NullBooleanField(default=None),
        ),
    ]
