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
                ('order', models.PositiveIntegerField(unique=True)),
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
            name='Compensation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
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
                ('title', models.CharField(help_text=b'Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', unique=True, max_length=200, verbose_name=b'Wat is de titel van uw studie?')),
                ('tech_summary', models.TextField(verbose_name=b'Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over proefpersonen, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi\xc3\xabnten van de methode meer gedetailleerde informatie worden gevraagd.')),
                ('supervisor_email', models.EmailField(help_text=b'Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=75, verbose_name=b'E-mailadres eindverantwoordelijke', blank=True)),
                ('other_applicants', models.BooleanField(default=False, verbose_name=b'Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?')),
                ('longitudinal', models.BooleanField(default=False, verbose_name=b'Is dit een studie waarbij dezelfde proefpersonen op meerdere dagen aan een sessie deelnemen? (bijvoorbeeld een longitudinale studie, of een kortlopende studie waar proefpersonen op twee of meer verschillende dagen getest worden)')),
                ('tasks_number', models.PositiveIntegerField(help_text=b'Wanneer u bijvoorbeeld eerst de proefpersoon observeert en de proefpersoon vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name=b'Hoeveel taken worden er binnen deze studie bij de proefpersoon afgenomen?')),
                ('tasks_duration', models.PositiveIntegerField(null=True, verbose_name=b'De totale geschatte netto taakduur van Uw sessie komt op basis van uw opgave per taak uit op <strong>%d minuten</strong>. Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)')),
                ('tasks_stressful', models.NullBooleanField(verbose_name=b'Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collegas, bij de proefpersonen zelf, bij derden)? Denk hierbij bijvoorbeeld aan de totale duur, vermoeidheid, etc. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de meest kwetsbare c.q. minst belastbare proefpersonengroep.')),
                ('informed_consent_pdf', models.FileField(upload_to=b'', verbose_name=b'Upload hier de informed consent', blank=True)),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, b'Algemene informatie ingevuld'), (2, b'WMO: in afwachting beslissing'), (3, b'WMO: afgerond'), (4, b'Kenmerken studie toegevoegd'), (5, b'Belasting proefpersoon: taken toevoegen'), (6, b'Belasting proefpersoon: alle taken toegevoegd'), (7, b'Belasting proefpersoon: afgerond'), (8, b'Informed consent geupload'), (9, b'Opgestuurd')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_submitted', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recruitment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
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
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
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
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
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
                ('has_traits', models.BooleanField(default=False, verbose_name=b'Proefpersonen kunnen geselecteerd worden op bepaalde bijzondere kenmerken die mogelijk samenhangen met een verhoogde kwetsbaarheid of verminderde belastbaarheid t.a.v. aspecten van de beoogde studie (bijvoorbeeld: kinderen die vroeger gepest zijn in een onderzoek naar de neurale reactie op verbale beledigingen; pati\xc3\xabnten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). Is dit in uw studie bij (een deel van) de proefpersonen het geval?')),
                ('traits_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('necessity', models.NullBooleanField(default=True, help_text=b'Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?', verbose_name=b'Is het om de onderzoeksvraag beantwoord te krijgen noodzakelijk om het geselecteerde type proefpersonen aan de studie te laten deelnemen?')),
                ('necessity_reason', models.TextField(verbose_name=b'Leg uit waarom', blank=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('risk_physical', models.NullBooleanField(default=False, verbose_name=b'Is de kans dat de proefpersoon fysiek letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?')),
                ('risk_psychological', models.NullBooleanField(default=False, verbose_name=b'Is de kans dat de proefpersoon psychisch letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?')),
                ('compensation_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('recruitment_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
                ('age_groups', models.ManyToManyField(to='proposals.AgeGroup', verbose_name=b'Geef hieronder aan binnen welke leeftijdscategorie uw proefpersonen vallen, er zijn meerdere antwoorden mogelijk')),
                ('compensation', models.ForeignKey(verbose_name=b'Welke vergoeding krijgt de proefpersoon voor zijn/haar deelname aan deze studie?', to='proposals.Compensation', help_text=b'tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld')),
                ('recruitment', models.ManyToManyField(to='proposals.Recruitment', verbose_name=b'Hoe worden de proefpersonen geworven?')),
                ('setting', models.ManyToManyField(to='proposals.Setting', verbose_name=b'Geef aan waar de dataverzameling plaatsvindt')),
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
                ('study', models.ForeignKey(to='proposals.Study')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Wat is de naam of korte beschrijving van de taak? (geef alleen een naam als daarmee volledig duidelijk is waar het om gaat, bijv "lexicale decisietaak")')),
                ('duration', models.PositiveIntegerField(verbose_name=b'Wat is de duur van deze taak van begin tot eind in minuten, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.')),
                ('actions_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('registrations_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('feedback', models.BooleanField(default=False, verbose_name=b'Krijgt de proefpersoon tijdens of na deze taak feedback op zijn/haar gedrag of toestand?')),
                ('feedback_details', models.CharField(max_length=200, verbose_name=b'Van welke aard is deze feedback?', blank=True)),
                ('stressful', models.NullBooleanField(default=False, verbose_name=b'Is deze taak belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collegas, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. En ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.')),
                ('actions', models.ManyToManyField(to='proposals.Action', verbose_name=b'Wat vraag je bij deze taak de proefpersoon te doen?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
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
                ('metc', models.NullBooleanField(verbose_name=b'Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?')),
                ('metc_institution', models.CharField(max_length=200, verbose_name=b'Welke instelling?', blank=True)),
                ('is_medical', models.NullBooleanField(default=False, verbose_name=b'Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?')),
                ('is_behavioristic', models.NullBooleanField(default=False, help_text=b'Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.', verbose_name=b'Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?')),
                ('metc_application', models.BooleanField(default=False, verbose_name=b'Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?')),
                ('metc_decision', models.BooleanField(default=False, verbose_name=b'Is de METC al tot een beslissing gekomen?')),
                ('metc_decision_pdf', models.FileField(upload_to=b'', verbose_name=b'Upload hier de beslissing van het METC', blank=True)),
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
            field=models.ManyToManyField(to='proposals.Registration', verbose_name=b'Hoe wordt het gedrag of de toestand van de proefpersoon bij deze taak vastgelegd?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='proposals.Trait', verbose_name=b'Selecteer de bijzondere kenmerken van uw proefpersonen', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(related_name='applicants', verbose_name=b'Uitvoerende(n)', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(to='proposals.Proposal', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='relation',
            field=models.ForeignKey(verbose_name=b'Wat is uw relatie tot het UiL OTS?', to='proposals.Relation'),
            preserve_default=True,
        ),
    ]
