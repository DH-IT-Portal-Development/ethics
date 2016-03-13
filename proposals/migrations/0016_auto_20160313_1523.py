# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0015_auto_20160313_0730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intervention',
            name='count',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='relation',
        ),
        migrations.AddField(
            model_name='intervention',
            name='has_drawbacks',
            field=models.BooleanField(default=False, help_text='Denk aan een verminderde leeropbrengst, een minder effectief 112-gesprek, een slechter adviesgesprek, een ongunstiger beoordeling, etc', verbose_name='Is de interventie zodanig dat er voor de deelnemers ook nadelen aan verbonden kunnen zijn?'),
        ),
        migrations.AddField(
            model_name='intervention',
            name='has_drawbacks_details',
            field=models.CharField(max_length=200, verbose_name='Licht toe', blank=True),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='description',
            field=models.TextField(verbose_name='Beschrijf de interventie. Geef daarbij aan in welke precieze setting(s) in hoe veel sessies welke precieze veranderingen worden doorgevoerd, en welke partijen er bij betrokken zijn.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='risk_details',
            field=models.TextField(max_length=200, verbose_name='Licht toe', blank=True),
        ),
    ]
