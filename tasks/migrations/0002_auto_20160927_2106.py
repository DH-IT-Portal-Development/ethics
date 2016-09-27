# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(verbose_name='Beschrijf de taak die de deelnemer moet uitvoeren, en leg kort uit hoe deze taak (en de eventuele manipulaties daarbinnen) aan de beantwoording van uw onderzoeksvragen bijdraagt. Geef, kort, een paar voorbeelden (of beschrijvingen) van het type stimuli dat u van plan bent aan de deelnemer aan te bieden. Het moet voor de commissieleden duidelijk zijn wat u precies gaat doen.'),
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), geef dan <strong>het redelijkerwijs te verwachten maximum op</strong>.', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
