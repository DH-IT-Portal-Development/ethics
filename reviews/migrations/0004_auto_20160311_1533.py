# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_review_continuation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='continuation',
            field=models.PositiveIntegerField(default=0, verbose_name='Afhandeling', choices=[(0, 'Goedkeuring door ETCL'), (1, 'Afwijzing door ETCL'), (2, 'Open review met lange (4-weken) route'), (3, 'Laat opnieuw beoordelen door METC')]),
        ),
    ]
