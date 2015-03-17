# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recruitment',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setting',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trait',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
