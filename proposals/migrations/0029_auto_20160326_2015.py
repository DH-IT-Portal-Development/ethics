# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0028_auto_20160326_2013'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setting',
            old_name='requires_supervision',
            new_name='needs_supervision',
        ),
    ]
