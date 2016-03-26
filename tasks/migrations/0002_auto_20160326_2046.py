# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='feedback',
            field=models.NullBooleanField(verbose_name='Krijgt de deelnemer tijdens of na deze taak feedback op zijn/haar gedrag of toestand?'),
        ),
    ]
