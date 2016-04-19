# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0012_auto_20160419_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Naam vragenlijst')),
                ('minutes', models.PositiveIntegerField(verbose_name='Duur (in minuten)')),
                ('survey_url', models.URLField(verbose_name='URL', blank=True)),
                ('description', models.TextField(verbose_name='Korte beschrijving')),
            ],
        ),
        migrations.AddField(
            model_name='study',
            name='has_surveys',
            field=models.BooleanField(default=False, verbose_name='Worden er vragenlijsten afgenomen bij <em>een ander dan de deelnemer</em>? Denk hierbij aan de ouder of voogd van een kind, de leraar van de klas, de arts van een pati\xebnt, etc.'),
        ),
        migrations.AddField(
            model_name='study',
            name='surveys_stressful',
            field=models.NullBooleanField(default=False, verbose_name='Is het invullen van deze vragenlijsten belastend? Denk hierbij bijv. aan het type vragen dat gesteld wordt en aan de tijd die de persoon kwijt is met het invullen van alle vragenlijsten.'),
        ),
        migrations.AddField(
            model_name='survey',
            name='study',
            field=models.ForeignKey(to='studies.Study'),
        ),
    ]
