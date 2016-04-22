# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0014_auto_20160420_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='name',
            field=models.CharField(max_length=15, verbose_name='Naam traject', blank=True),
        ),
    ]
