# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0020_auto_20160603_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='survey',
            name='study',
        ),
        migrations.RemoveField(
            model_name='study',
            name='has_surveys',
        ),
        migrations.RemoveField(
            model_name='study',
            name='surveys_stressful',
        ),
        migrations.DeleteModel(
            name='Survey',
        ),
    ]
