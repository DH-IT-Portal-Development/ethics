# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='created_by',
            new_name='submitter',
        ),
        migrations.AddField(
            model_name='feedback',
            name='date_modified',
            field=models.DateField(default=datetime.datetime(2015, 6, 12, 13, 45, 2, 539513, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='priority',
            field=models.IntegerField(default=1, choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedback',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Open'), (2, 'Working'), (3, 'Closed')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='comment',
            field=models.TextField(verbose_name=b'Opmerking'),
            preserve_default=True,
        ),
    ]
