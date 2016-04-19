# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0006_auto_20160419_1338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='study',
            name='sessions_duration',
        ),
    ]
