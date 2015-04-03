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
                ('title', models.CharField(help_text=b'Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', unique=True, max_length=200, verbose_name=b'Titel studie')),
                ('tech_summary', models.TextField(help_text=b'Schrijf hier een samenvatting van max. 500 woorden. Deze samenvatting moet in ieder geval bestaan uit een duidelijke beschrijving van deonderzoeksvraag, de proefpersonen. Geef een helder beeld van de procedure en een beschrijving van de stimuli (indien daar sprake van is), het aantal taken en de methode waarmee het gedrag van de proefpersoon wordt vastgelegd (bijv.: reactietijden; knoppenbox; schriftelijke vragenlijst; interview; etc.).', verbose_name=b'Samenvatting')),
                ('supervisor_email', models.EmailField(help_text=b'Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=75, verbose_name=b'E-mailadres eindverantwoordelijke', blank=b'True')),
                ('other_applicants', models.BooleanField(default=False, verbose_name=b'Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?')),
                ('longitudinal', models.BooleanField(default=False, verbose_name=b'Is dit een studie waarbij dezelfde proefpersonen op meerdere dagen aan een sessie deelnemen? (bijvoorbeeld een longitudinale studie, of een kortlopende studie waar proefpersonen op twee of meer verschillende dagen getest worden)')),
                ('informed_consent_pdf', models.FileField(upload_to=b'', verbose_name=b'Upload hier de informed consent', blank=True)),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, b'draft'), (2, b'wmo_awaiting_decision'), (3, b'wmo_finished'), (4, b'study'), (5, b'tasks'), (6, b'informed_consent_uploaded'), (7, b'submitted')])),
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
                ('has_traits', models.BooleanField(default=False, verbose_name=b'Proefpersonen kunnen geselecteerd worden op bepaalde bijzondere kenmerken die mogelijk samenhangen met een verhoogde kwetsbaarheid of verminderde belastbaarheid t.a.v. aspecten van de beoogde studie (bijvoorbeeld: kinderen die vroeger gepest zijn in een onderzoek naar de neurale reactie op verbale beledigingen; pati&#235;nten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). Is dit in uw studie bij (een deel van) de proefpersonen het geval?')),
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
                ('setting', models.ForeignKey(verbose_name=b'Geef aan waar de studie plaatsvindt', to='proposals.Setting')),
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
                ('name', models.CharField(max_length=200, verbose_name=b'Naam van de taak')),
                ('procedure', models.NullBooleanField(verbose_name=b'Welk onderdeel, of welke combinatie van onderdelen, van de procedure zouden door de proefpersonen als belastend/onaangenaam ervaren kunnen worden?')),
                ('duration', models.PositiveIntegerField(verbose_name=b'Wat is de duur van de taak, waarbij de proefpersoon een handeling moet verrichten, van begin tot eind, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak?')),
                ('registrations_details', models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True)),
                ('actions', models.ManyToManyField(to='proposals.Action', verbose_name=b'Geef aan welke handeling de proefpersoon moet uitvoeren of aan welke gedragsregel de proefpersoon wordt onderworpen')),
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
                ('metc', models.NullBooleanField(default=False, verbose_name=b'Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?')),
                ('metc_institution', models.CharField(max_length=200, verbose_name=b'Welke instelling?', blank=True)),
                ('is_medical', models.NullBooleanField(default=False, verbose_name=b'Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?')),
                ('is_behavioristic', models.NullBooleanField(default=False, help_text=b'Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.', verbose_name=b'Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?')),
                ('metc_application', models.BooleanField(default=False, verbose_name=b'Uw studie moet beoordeeld worden door de METC<link>, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?')),
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
            field=models.ManyToManyField(to='proposals.Registration', verbose_name=b'Hoe worden de gegevens vastgelegd? Door middel van:'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='proposals.Trait', verbose_name=b'Selecteer de bijzondere kenmerken van uw proefpersonen'),
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
