# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_auto_20160422_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='wmo',
            name='metc_details',
            field=models.TextField(verbose_name='Licht toe', blank=True),
        ),
    ]
