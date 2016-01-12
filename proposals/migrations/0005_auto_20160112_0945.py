# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0004_auto_20160112_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='legally_incapable',
            field=models.BooleanField(default=False, verbose_name=' Maakt uw studie gebruik van wilsonbekwame proefpersonen?'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Naam vragenlijst'),
        ),
    ]
