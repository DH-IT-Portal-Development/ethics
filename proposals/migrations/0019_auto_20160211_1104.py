# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0018_auto_20160210_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='age_min',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.BooleanField(default=False, verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wilsonbekwame deelnemers?'),
        ),
    ]
