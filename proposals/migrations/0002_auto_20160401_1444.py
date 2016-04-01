# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='has_multiple_groups',
            field=models.NullBooleanField(help_text='Een deelnemersgroep kan gekenmerkt worden door een controle- en experimentele groep, maar ook door twee verschillende leeftijden (0-2 jarigen en volwassenen of 18-22 jarigen en 35-40 jarigen)', verbose_name='Is er in uw studie sprake van verschillende deelnemersgroepen?'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='has_multiple_trajectories',
            field=models.NullBooleanField(help_text="Een traject is verschillend wanneer u bijvoorbeeld baby's \xe9n volwassenen test op hun discriminatievaardigheden, maar zij krijgen een ander type taak. Er is ook sprake van een ander traject wanneer u een groep 18-22 jarigen sessie A, B en C laat doen, terwijl de 35-40 jarigen alleen C doen.", verbose_name='Lopen deze groepen een verschillend traject door?'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='studies_number',
            field=models.PositiveIntegerField(null=True, verbose_name='Hoeveel verschillende trajecten zijn er?', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
