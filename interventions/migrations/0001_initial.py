# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('supervision', models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?')),
                ('period', models.TextField(verbose_name='Wat is de periode waarbinnen de interventie plaatsvindt?')),
                ('amount_per_week', models.PositiveIntegerField(verbose_name='Hoe vaak per week vindt de interventiesessie plaats?')),
                ('duration', models.PositiveIntegerField(verbose_name='Wat is de duur van de interventie per sessie in minuten?')),
                ('experimenter', models.TextField(verbose_name='Wie voert de interventie uit?')),
                ('description', models.TextField(verbose_name='Geef een beschrijving van de experimentele interventie')),
                ('has_controls', models.BooleanField(default=False, verbose_name='Is er sprake van een controlegroep?')),
                ('controls_description', models.TextField(verbose_name='Geef een beschrijving van de controleinterventie', blank=True)),
                ('measurement', models.TextField(help_text='Wanneer u de deelnemer extra taken laat uitvoeren, dus een taak die niet behoort tot het reguliere onderwijspakket, dan moet u op de vorige pagina ook "takenonderzoek" aanvinken.', verbose_name='Hoe wordt het effect van de interventie gemeten?')),
                ('setting', models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt')),
                ('study', models.OneToOneField(to='studies.Study', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
