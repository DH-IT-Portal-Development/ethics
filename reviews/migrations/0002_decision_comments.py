# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='comments',
            field=models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True),
        ),
    ]
