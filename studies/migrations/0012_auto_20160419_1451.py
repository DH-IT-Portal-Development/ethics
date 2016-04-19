# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0011_study_setting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='study',
            name='setting',
        ),
        migrations.RemoveField(
            model_name='study',
            name='setting_details',
        ),
        migrations.RemoveField(
            model_name='study',
            name='supervision',
        ),
    ]
