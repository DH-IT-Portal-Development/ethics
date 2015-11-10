# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0014_auto_20151009_1327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='supervisor_comments',
        ),
    ]
