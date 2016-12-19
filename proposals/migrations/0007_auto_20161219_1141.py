# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0006_proposal_is_pre_assessment'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='is_exploration',
            field=models.BooleanField(default=False, verbose_name='Ik vul de portal in om de portal te exploreren'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='in_course',
            field=models.BooleanField(default=False, verbose_name='Ik vul de portal in in het kader van een cursus'),
        ),
    ]
