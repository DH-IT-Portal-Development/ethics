# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='name',
            field=models.CharField(default='', max_length=200, verbose_name='Wat is de naam van deze deelnemersgroep?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='study',
            name='order',
            field=models.PositiveIntegerField(default=1, unique=True),
            preserve_default=False,
        ),
    ]
