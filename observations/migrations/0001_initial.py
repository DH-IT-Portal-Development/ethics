# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.validators
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('supervision', models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?')),
                ('days', models.PositiveIntegerField(verbose_name='Op hoeveel dagen wordt er geobserveerd (per deelnemer)?')),
                ('mean_hours', models.DecimalField(verbose_name='Hoeveel uur wordt er gemiddeld per dag geobserveerd?', max_digits=4, decimal_places=2, validators=[django.core.validators.MaxValueValidator(24)])),
                ('is_anonymous', models.BooleanField(default=False, help_text='Zoals zou kunnen voorkomen op fora en de onderzoeker ook een account heeft.', verbose_name='Wordt er anoniem geobserveerd?')),
                ('is_in_target_group', models.BooleanField(default=False, verbose_name='Doet de onderzoeker zich voor als behorende tot de doelgroep?')),
                ('is_nonpublic_space', models.BooleanField(default=False, help_text='Bijvoorbeeld er wordt geobserveerd bij iemand thuis, tijdens een hypotheekgesprek, tijdens politieverhoren of een forum waar een account voor moet worden aangemaakt.', verbose_name='Wordt er geobserveerd in een niet-openbare ruimte?')),
                ('has_advanced_consent', models.BooleanField(default=True, verbose_name='Vindt informed consent van tevoren plaats?')),
                ('needs_approval', models.BooleanField(default=False, verbose_name='Heeft u toestemming nodig van een (samenwerkende) instantie om deze observatie te mogen uitvoeren?')),
                ('approval_institution', models.CharField(max_length=200, verbose_name='Welke instantie?', blank=True)),
                ('approval_document', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier het toestemmingsdocument (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc])),
                ('registrations_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='observation',
            name='registrations',
            field=models.ManyToManyField(to='observations.Registration', verbose_name='Hoe wordt het gedrag geregistreerd?'),
        ),
        migrations.AddField(
            model_name='observation',
            name='setting',
            field=models.ManyToManyField(to='core.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt'),
        ),
        migrations.AddField(
            model_name='observation',
            name='study',
            field=models.OneToOneField(to='studies.Study'),
        ),
    ]
