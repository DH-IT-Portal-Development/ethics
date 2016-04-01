# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Funding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_number', models.CharField(unique=True, max_length=16)),
                ('date_start', models.DateField(verbose_name='Wat is de beoogde startdatum van uw studie?')),
                ('title', models.CharField(help_text='Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', unique=True, max_length=200, verbose_name='Wat is de titel van uw studie?')),
                ('summary', models.TextField(verbose_name='Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.', validators=[core.validators.MaxWordsValidator(200)])),
                ('other_applicants', models.BooleanField(default=False, verbose_name='Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?')),
                ('other_stakeholders', models.BooleanField(default=False, verbose_name='Zijn er onderzoekers van buiten UiL OTS bij deze studie betrokken?')),
                ('stakeholders', models.TextField(verbose_name='Andere betrokkenen', blank=True)),
                ('funding_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('comments', models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True)),
                ('has_surveys', models.BooleanField(default=False, verbose_name='Worden er vragenlijsten afgenomen bij <em>een ander dan de deelnemer</em>? Denk hierbij aan de ouder of voogd van een kind, de leraar van de klas, de arts van een pati\xebnt, etc.')),
                ('surveys_stressful', models.NullBooleanField(default=False, verbose_name='Is het invullen van deze vragenlijsten belastend? Denk hierbij bijv. aan het type vragen dat gesteld wordt en aan de tijd die de persoon kwijt is met het invullen van alle vragenlijsten.')),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Informed consent toegevoegd'), (6, 'Opzet studie: gestart'), (10, 'Nadere specificatie van het interventieonderdeel'), (20, 'Nadere specificatie van het observatieonderdeel'), (30, 'Nadere specificatie van het takenonderdeel'), (31, 'Takenonderdeel: taken toevoegen'), (32, 'Takenonderdeel: alle taken toegevoegd'), (33, 'Takenonderdeel: afgerond'), (34, 'Opzet studie: afgerond'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Studie is beoordeeld door ETCL'), (60, 'Studie is beoordeeld door METC')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_submitted_supervisor', models.DateTimeField(null=True)),
                ('date_reviewed_supervisor', models.DateTimeField(null=True)),
                ('date_submitted', models.DateTimeField(null=True)),
                ('date_reviewed', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_supervisor', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
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
        migrations.CreateModel(
            name='Wmo',
            fields=[
                ('metc', models.NullBooleanField(verbose_name='Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?')),
                ('metc_institution', models.CharField(max_length=200, verbose_name='Welke instelling?', blank=True)),
                ('is_medical', models.NullBooleanField(help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?')),
                ('is_behavioristic', models.NullBooleanField(help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken.', verbose_name='Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?')),
                ('metc_application', models.BooleanField(default=False, verbose_name='Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al aangemeld bij een METC?')),
                ('metc_decision', models.BooleanField(default=False, verbose_name='Is de METC al tot een beslissing gekomen?')),
                ('metc_decision_pdf', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de beslissing van het METC (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc])),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Geen beoordeling door METC noodzakelijk'), (1, 'In afwachting beslissing METC'), (2, 'Beslissing METC ge\xfcpload')])),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
            ],
        ),
        migrations.AddField(
            model_name='survey',
            name='proposal',
            field=models.ForeignKey(to='proposals.Proposal'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(help_text='Als uw medeonderzoeker niet in de lijst voorkomt, vraag hem dan een keer in te loggen in het webportaal.', related_name='applicants', verbose_name='Uitvoerende(n)', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='proposal',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='proposal',
            name='funding',
            field=models.ManyToManyField(to='proposals.Funding', verbose_name='Hoe wordt dit onderzoek gefinancierd?'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(verbose_name='Te kopi\xebren studie', to='proposals.Proposal', help_text='Dit veld toont enkel studies waar u zelf een medeuitvoerende bent.', null=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='relation',
            field=models.ForeignKey(verbose_name='Wat is uw relatie tot het UiL OTS?', to='proposals.Relation'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='supervisor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Aan het einde van de procedure kunt u deze studie ter verificatie naar uw eindverantwoordelijke sturen. De eindverantwoordelijke zal de studie vervolgens kunnen aanpassen en indienen bij de ETCL.', null=True, verbose_name='Eindverantwoordelijke onderzoeker'),
        ),
    ]
