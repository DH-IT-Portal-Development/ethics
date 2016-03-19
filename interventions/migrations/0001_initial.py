# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0021_auto_20160319_1404'),
    ]

    operations = [
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(verbose_name='Beschrijf de interventie. Geef daarbij aan in welke precieze setting(s) in hoe veel sessies welke precieze veranderingen worden doorgevoerd, en welke partijen er bij betrokken zijn.')),
                ('has_drawbacks', models.BooleanField(default=False, help_text='Denk aan een verminderde leeropbrengst, een minder effectief 112-gesprek, een slechter adviesgesprek, een ongunstiger beoordeling, etc', verbose_name='Is de interventie zodanig dat er voor de deelnemers ook nadelen aan verbonden kunnen zijn?')),
                ('has_drawbacks_details', models.CharField(max_length=200, verbose_name='Licht toe', blank=True)),
                ('study', models.OneToOneField(to='proposals.Study')),
            ],
        ),
    ]
