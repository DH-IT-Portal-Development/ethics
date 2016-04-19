# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('observations', '0005_auto_20160408_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='setting',
            field=models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt'),
        ),
        migrations.AddField(
            model_name='observation',
            name='setting_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='supervision',
            field=models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?'),
        ),
    ]
