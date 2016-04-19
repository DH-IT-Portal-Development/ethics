# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('studies', '0010_auto_20160419_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='setting',
            field=models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt'),
        ),
    ]
