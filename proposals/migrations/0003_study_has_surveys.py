# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_auto_20160211_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='has_surveys',
            field=models.BooleanField(default=False, verbose_name='Worden er vragenlijsten afgenomen bij <em>een ander dan de deelnemer</em>? Denk hierbij aan de ouder of voogd van een kind, de leraar van de klas, de arts van een pati\xebnt, etc.'),
        ),
    ]
