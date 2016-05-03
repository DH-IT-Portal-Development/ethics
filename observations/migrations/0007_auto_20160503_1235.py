# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0006_auto_20160419_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='observation',
        ),
        migrations.RemoveField(
            model_name='location',
            name='registrations',
        ),
        migrations.AddField(
            model_name='observation',
            name='registrations',
            field=models.ManyToManyField(to='observations.Registration', verbose_name='Hoe wordt het gedrag geregistreerd?'),
        ),
        migrations.AddField(
            model_name='observation',
            name='registrations_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
