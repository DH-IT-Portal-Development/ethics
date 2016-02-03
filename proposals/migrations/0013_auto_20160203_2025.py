# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0012_auto_20160202_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='study',
            name='traits',
        ),
        migrations.RemoveField(
            model_name='study',
            name='traits_details',
        ),
        migrations.DeleteModel(
            name='Trait',
        ),
    ]
