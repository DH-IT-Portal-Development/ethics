# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='continuation',
            field=models.PositiveIntegerField(default=0, verbose_name='Afhandeling', choices=[(0, 'Goedkeuring door ETCL'), (1, 'Revisie noodzakelijk'), (2, 'Afwijzing door ETCL'), (3, 'Open review met lange (4-weken) route'), (4, 'Laat opnieuw beoordelen door METC')]),
        ),
    ]
