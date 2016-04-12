# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0002_auto_20160408_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervention',
            name='has_drawbacks',
            field=models.BooleanField(help_text='Denk aan een verminderde leeropbrengst, een minder effectief 112-gesprek, een slechter adviesgesprek, een ongunstiger beoordeling, etc', verbose_name='Is de interventie zodanig dat er voor de deelnemers ook nadelen aan verbonden kunnen zijn?'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='has_drawbacks_details',
            field=models.TextField(verbose_name='Licht toe', blank=True),
        ),
    ]
