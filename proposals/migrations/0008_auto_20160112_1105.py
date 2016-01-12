# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0007_auto_20160112_1045'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='end_date',
            new_name='date_end',
        ),
        migrations.RenameField(
            model_name='proposal',
            old_name='start_date',
            new_name='date_start',
        ),
    ]
