# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('tasks', '0002_auto_20160419_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='setting',
            field=models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt'),
        ),
        migrations.AddField(
            model_name='session',
            name='setting_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.AddField(
            model_name='session',
            name='supervision',
            field=models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?'),
        ),
    ]
