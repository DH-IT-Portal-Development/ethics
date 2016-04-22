# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0007_auto_20160419_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='studies_number',
            field=models.PositiveIntegerField(default=1, verbose_name='Hoeveel verschillende trajecten zijn er?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
