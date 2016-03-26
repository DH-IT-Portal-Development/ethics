# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0027_auto_20160326_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='requires_supervision',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='study',
            name='supervision',
            field=models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?'),
        ),
    ]
