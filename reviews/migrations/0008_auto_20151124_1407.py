# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0007_auto_20151113_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='stage',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Beoordeling door supervisor'), (1, 'Aanstelling commissieleden'), (2, 'Beoordeling door ethische commissie')]),
        ),
    ]
