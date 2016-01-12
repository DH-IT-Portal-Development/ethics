# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0006_survey_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2016, 1, 12, 9, 45, 14, 400347, tzinfo=utc), verbose_name='Wat is de beoogde einddatum van uw studie?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proposal',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2016, 1, 12, 9, 45, 20, 656343, tzinfo=utc), verbose_name='Wat is de beoogde startdatum van uw studie?'),
            preserve_default=False,
        ),
    ]
