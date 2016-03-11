# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0009_auto_20160303_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation', models.CharField(max_length=200, verbose_name='Wat is de relatie tot de proefpersoon?')),
                ('count', models.CharField(max_length=200, verbose_name='Hoe vaak wordt die instructie gegeven?')),
                ('description', models.TextField(verbose_name='Beschrijf de interventie.')),
                ('study', models.ForeignKey(to='proposals.Study')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Locatie')),
                ('registration', models.TextField(verbose_name='Hoe wordt het gedrag geregistreerd?')),
            ],
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('days', models.PositiveIntegerField(verbose_name='Op hoeveel dagen wordt er geobserveerd?')),
                ('mean_hours', models.DecimalField(verbose_name='Hoeveel uur wordt er gemiddeld per dag geobserveerd?', max_digits=4, decimal_places=2, validators=[django.core.validators.MaxValueValidator(24)])),
                ('is_anonymous', models.BooleanField(default=False, help_text='Zoals zou kunnen voorkomen op fora en de onderzoeker ook een account heeft.', verbose_name='Weten de deelnemers dat ze deelnemer zijn, ofwel, wordt er anoniem geobserveerd?')),
                ('is_test', models.BooleanField(default=False, verbose_name='Doet de onderzoeker zich voor als behorende tot de doelgroep?')),
                ('study', models.ForeignKey(to='proposals.Study')),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='observation',
            field=models.ForeignKey(to='proposals.Observation'),
        ),
    ]
