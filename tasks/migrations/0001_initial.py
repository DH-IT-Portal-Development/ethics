# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('needs_kind', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
                ('age_min', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='RegistrationKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
                ('registration', models.ForeignKey(to='tasks.Registration', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('supervision', models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?')),
                ('order', models.PositiveIntegerField()),
                ('tasks_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer observeert en de deelnemer vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name='Hoeveel taken worden er binnen deze sessie bij de deelnemer afgenomen?', validators=[django.core.validators.MinValueValidator(1)])),
                ('tasks_duration', models.PositiveIntegerField(null=True, verbose_name='De totale geschatte netto taakduur van uw sessie komt op basis van uw opgave per taak uit op <strong>%d minuten</strong>. Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)')),
                ('setting', models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt')),
                ('study', models.ForeignKey(to='studies.Study', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=200, verbose_name='Wat is de naam van de taak?')),
                ('description', models.TextField(verbose_name='Beschrijf de taak die de deelnemer moet uitvoeren, en leg kort uit hoe deze taak (en de eventuele manipulaties daarbinnen) aan de beantwoording van uw onderzoeksvragen bijdraagt.')),
                ('duration', models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1)])),
                ('registrations_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('registration_kinds_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('feedback', models.NullBooleanField(verbose_name='Krijgt de deelnemer tijdens of na deze taak feedback op zijn/haar gedrag of toestand?')),
                ('feedback_details', models.TextField(verbose_name='Beschrijf hoe de feedback wordt gegeven.', blank=True)),
                ('registration_kinds', models.ManyToManyField(to='tasks.RegistrationKind', verbose_name='Kies het soort meting', blank=True)),
                ('registrations', models.ManyToManyField(to='tasks.Registration', verbose_name='Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?')),
                ('session', models.ForeignKey(to='tasks.Session', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('session', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([('study', 'order')]),
        ),
    ]
