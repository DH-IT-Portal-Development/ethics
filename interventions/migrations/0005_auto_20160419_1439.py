# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('interventions', '0004_auto_20160408_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervention',
            name='setting',
            field=models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt'),
        ),
        migrations.AddField(
            model_name='intervention',
            name='setting_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='supervision',
            field=models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?'),
        ),
    ]
