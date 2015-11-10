# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_decision_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='stage',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Beoordeling door supervisor'), (1, 'Beoordeling door ethische commissie')]),
        ),
    ]
