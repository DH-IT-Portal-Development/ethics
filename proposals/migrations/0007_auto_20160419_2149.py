# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0006_auto_20160419_1557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='survey',
            name='proposal',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='has_surveys',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='surveys_stressful',
        ),
        migrations.DeleteModel(
            name='Survey',
        ),
    ]
