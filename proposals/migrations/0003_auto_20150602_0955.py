# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_auto_20150526_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ['-order']},
        ),
        migrations.AddField(
            model_name='proposal',
            name='reference_number',
            field=models.CharField(default='test', unique=True, max_length=16),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(default=0, verbose_name=b'Wat is de duur van deze taak van begin tot eind in minuten, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
    ]
