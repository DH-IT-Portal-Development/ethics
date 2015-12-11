# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0021_auto_20151208_1640'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='survey',
            name='survey_file',
        ),
    ]
