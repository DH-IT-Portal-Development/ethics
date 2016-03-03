# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='short_route',
            field=models.BooleanField(default=True, verbose_name='Route'),
        ),
        migrations.AlterField(
            model_name='review',
            name='stage',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Beoordeling door eindverantwoordelijke'), (1, 'Aanstelling commissieleden'), (2, 'Beoordeling door ethische commissie')]),
        ),
    ]
