# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0004_auto_20160419_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='has_multiple_groups',
        ),
    ]
