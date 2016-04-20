# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0013_auto_20160419_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='name',
            field=models.CharField(default='', max_length=15, verbose_name='Wat is de naam van deze deelnemersgroep?'),
            preserve_default=False,
        ),
    ]
