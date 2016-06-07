# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20160607_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='stage',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Beoordeling door eindverantwoordelijke'), (1, 'Aanstelling commissieleden'), (2, 'Beoordeling door commissie'), (3, 'Afsluiting door secretaris')]),
        ),
    ]
