# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('info_text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AgeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('age_min', models.PositiveIntegerField()),
                ('age_max', models.PositiveIntegerField(null=True, blank=True)),
                ('description', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('question', models.TextField()),
                ('answer', models.TextField()),
            ],
            options={
                'verbose_name': 'FAQ',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('deadline', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Een studie wordt als volgt gedefinieerd: proefpersonen worden aan eenzelfde handeling of reeks handelingen onderworpen. Dus proefpersonen binnen de studie, ongeacht de groep (controle of  experimentele groep), doen allemaal dezelfde taak/taken. Wanneer het om herhaalde metingen gaat en de procedure verandert per meetmoment, moeten er verschillende aanvragen worden ingediend bij de commissie via deze webportal. Ook wanneer de taken onveranderd blijven, maar de proefpersonen kruisen een leeftijdscategorie (--link leeftijdscategorieen--), moeten er meerdere aanvragen ingediend worden. Vragen 6 en 7 gaan hierover. Het is handig voor het overzicht en het aanvraagproces om in de titel van de studie de leeftijdscategorie te vermelden.', max_length=200, verbose_name=b'Titel studie')),
                ('tech_summary', models.TextField(help_text=b'Schrijf hier een samenvatting van max. 500 woorden. Deze samenvatting moet in ieder geval bestaan uit een duidelijke beschrijving van deonderzoeksvraag, de proefpersonen. Geef een helder beeld van de procedure en een beschrijving van de stimuli (indien daar sprake van is), het aantal taken en de methode waarmee het gedrag van de proefpersoon wordt vastgelegd (bijv.: reactietijden; knoppenbox; schriftelijke vragenlijst; interview; etc.).', verbose_name=b'Samenvatting')),
                ('longitudinal', models.BooleanField(default=False, verbose_name=b'Is uw studie een longitudinale studie?')),
                ('supervisor_name', models.CharField(help_text=b'De eindverantwoordelijke is een onderzoeker die de graad van doctor behaald heeft. Wanneer een student de aanvraag doet, dan is de eindverantwoordelijke de begeleidende onderzoeker met in ieder geval een doctorstitel.', max_length=200, verbose_name=b'Naam eindverantwoordelijke')),
                ('supervisor_email', models.EmailField(help_text=b'Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=75, verbose_name=b'E-mailadres eindverantwoordelijke')),
                ('status', models.PositiveIntegerField(choices=[(0, b'draft'), (1, b'wmo_'), (2, b'wmo_finished'), (2, b'participant_groups'), (3, b'experiments'), (4, b'concept'), (5, b'submitted')])),
                ('date_submitted', models.DateTimeField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recruitment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('traits_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('necessity', models.NullBooleanField(default=True, verbose_name=b'Is het noodzakelijk om deze geselecteerde groep proefpersonen aan de door jou opgelegde handeling te onderwerpen om de onderzoeksvraag beantwoord te krijgen? Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou je de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?')),
                ('necessity_reason', models.TextField(verbose_name=b'Leg uit waarom', blank=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('risk_physical', models.NullBooleanField(default=False, verbose_name=b'Is er een kans dat de proefpersoon fysiek letsel oploopt?')),
                ('risk_psychological', models.NullBooleanField(default=False, verbose_name=b'Is er een kans dat de proefpersoon psychisch letsel oploopt?')),
                ('compensation', models.CharField(help_text=b'tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld', max_length=200, verbose_name=b'Welke vergoeding krijgt de proefpersoon voor verrichte taken?')),
                ('recruitment_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
                ('age_groups', models.ManyToManyField(to='proposals.AgeGroup', verbose_name=b'Geef hieronder aan binnen welke leeftijdscategorie uw proefpersonen vallen, er zijn meerdere antwoorden zijn mogelijk')),
                ('recruitment', models.ManyToManyField(to='proposals.Recruitment', verbose_name=b'Hoe worden de proefpersonen geworven?')),
                ('setting', models.ManyToManyField(to='proposals.Setting', verbose_name=b'Geef aan waar de studie plaatsvindt')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('minutes', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Naam van de taak')),
                ('procedure', models.NullBooleanField(verbose_name=b'Welk onderdeel, of welke combinatie van onderdelen, van de procedure zouden door de proefpersonen als belastend/onaangenaam ervaren kunnen worden?')),
                ('duration', models.PositiveIntegerField(verbose_name=b'Wat is de duur van de taak, waarbij de proefpersoon een handeling moet verrichten, van begin tot eind, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak?')),
                ('registrations_details', models.CharField(max_length=200, blank=True)),
                ('actions', models.ManyToManyField(to='proposals.Action')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wmo',
            fields=[
                ('metc', models.NullBooleanField(default=False, verbose_name=b'Vindt de studie plaats binnen het UMC Utrecht, of een andere instelling waarbij de METC verplicht betrokken wordt?')),
                ('metc_institution', models.CharField(max_length=200, verbose_name=b'Instelling', blank=True)),
                ('is_medical', models.NullBooleanField(default=False, verbose_name=b'Is de onderzoeksvraag medisch-wetenschappelijk van aard?')),
                ('is_behavioristic', models.NullBooleanField(default=False, help_text=b'Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.', verbose_name=b'Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd?')),
                ('metc_decision', models.BooleanField(default=False, verbose_name=b'Is uw onderzoek al in behandeling genomen door een METC?')),
                ('metc_decision_pdf', models.FileField(upload_to=b'', verbose_name=b'Upload hier de beslissing van het METC')),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='task',
            name='proposal',
            field=models.ForeignKey(to='proposals.Proposal'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='registrations',
            field=models.ManyToManyField(to='proposals.Registration'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='study',
            name='surveys',
            field=models.ManyToManyField(to='proposals.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='proposals.Trait', verbose_name=b'Worden de beoogde proefpersonen op bijzondere kenmerken geselecteerden die mogelijk een negatief effect hebben op de kwetsbaarheid of verminderde belastbaarheid van de proefpersoon? Indien u twee (of meer) groepen voor ogen heeft, hoeft u over de controlegroep (die dus geen bijzondere kenmerken heeft) niet in het hoofd te nemen bij het beantwoorden van de ze vraag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Uitvoerende(n)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(to='proposals.Proposal', null=True),
            preserve_default=True,
        ),
    ]
