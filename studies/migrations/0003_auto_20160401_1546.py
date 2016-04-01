# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0002_auto_20160401_1504'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='study',
            options={'ordering': ['order']},
        ),
        migrations.AlterField(
            model_name='study',
            name='order',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='study',
            unique_together=set([('proposal', 'order')]),
        ),
    ]
