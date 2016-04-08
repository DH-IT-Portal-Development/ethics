# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0003_auto_20160408_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervention',
            name='has_drawbacks',
            field=models.BooleanField(default=False, help_text='Denk aan een verminderde leeropbrengst, een minder effectief 112-gesprek, een slechter adviesgesprek, een ongunstiger beoordeling, etc', verbose_name='Is de interventie zodanig dat er voor de deelnemers ook nadelen aan verbonden kunnen zijn?'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='is_supervised',
            field=models.BooleanField(default=True, verbose_name='Vindt de interventie plaats onder het toezicht van een een bevoegd persoon die, wanneer de interventie niet zou plaatsvinden, er ook zou zijn. Zoals een leraar of logopedist.'),
        ),
    ]
