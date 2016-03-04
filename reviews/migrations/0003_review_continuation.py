# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20160303_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='continuation',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Akkoord door ETCL'), (1, 'Geen akkoord door ETCL'), (2, 'Open review met lange (4-weken) route'), (3, 'Laat opnieuw beoordelen door METC')]),
        ),
    ]
