# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0010_auto_20170328_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='confirmation_comments',
            field=models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name='Datum bevestigingsbrief verstuurd'),
        ),
    ]
