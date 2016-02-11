# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='risk_details',
            field=models.TextField(verbose_name='Licht toe', blank=True),
        ),
    ]
