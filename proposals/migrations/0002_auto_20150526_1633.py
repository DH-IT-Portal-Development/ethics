# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ['order']},
        ),
        migrations.AlterField(
            model_name='session',
            name='order',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([('proposal', 'order')]),
        ),
    ]
