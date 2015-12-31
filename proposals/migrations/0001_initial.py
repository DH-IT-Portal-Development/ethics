# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import proposals.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('age_min', models.PositiveIntegerField()),
                ('age_max', models.PositiveIntegerField(null=True, blank=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('max_net_duration', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Compensation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
            ],
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
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_number', models.CharField(unique=True, max_length=16)),
                ('title', models.CharField(help_text='Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', unique=True, max_length=200, verbose_name='Wat is de titel van uw studie?')),
                ('tech_summary', models.TextField(verbose_name='Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over proefpersonen, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi\xebnten van de methode meer gedetailleerde informatie worden gevraagd.')),
                ('other_applicants', models.BooleanField(default=False, verbose_name='Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?')),
                ('longitudinal', models.BooleanField(default=False, verbose_name='Is dit een studie waarbij dezelfde proefpersonen op meerdere dagen deelnemen aan een sessie? (bijvoorbeeld een longitudinale studie, of een kortlopende studie waar proefpersonen op twee of meer verschillende dagen getest worden)')),
                ('comments', models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True)),
                ('sessions_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de proefpersoon een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de proefpersoon nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies telt deze studie?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('sessions_duration', models.PositiveIntegerField(help_text='Dit is de geschatte totale bruto tijd die de proefpersoon kwijt is aan alle sessie bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name='De totale geschatte netto studieduur van uw sessie komt op basis van uw opgave per sessie uit op <strong>%d minuten</strong>. Schat de totale tijd die uw proefpersonen aan de gehele studie zullen besteden.')),
                ('sessions_stressful', models.NullBooleanField(default=False, verbose_name="Is het totaal van sessies als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.")),
                ('sessions_stressful_details', models.TextField(verbose_name='Waarom denkt u dat?', blank=True)),
                ('informed_consent_pdf', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informed consent (in PDF-formaat)', validators=[proposals.models.validate_pdf])),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting proefpersoon: sessies toevoegen'), (6, 'Belasting proefpersoon: taken toevoegen'), (7, 'Belasting proefpersoon: alle taken toegevoegd'), (8, 'Belasting proefpersoon: afgerond'), (9, 'Belasting proefpersoon: afgerond'), (10, 'Informed consent ge\xfcpload'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Aanvraag is beoordeeld door ETCL'), (60, 'Aanvraag is beoordeeld door METC')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_submitted_supervisor', models.DateTimeField(null=True)),
                ('date_reviewed_supervisor', models.DateTimeField(null=True)),
                ('date_submitted', models.DateTimeField(null=True)),
                ('date_reviewed', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recruitment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('needs_kind', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('registration', models.ForeignKey(to='proposals.Registration')),
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
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('stressful', models.NullBooleanField(verbose_name="Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij bijvoorbeeld aan de totale duur, vermoeidheid, etc. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de meest kwetsbare c.q. minst belastbare proefpersonengroep.")),
                ('stressful_details', models.TextField(verbose_name=b'Waarom denkt u dat?', blank=True)),
                ('tasks_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de proefpersoon observeert en de proefpersoon vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name='Hoeveel taken worden er binnen deze sessie bij de proefpersoon afgenomen?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('tasks_duration', models.PositiveIntegerField(null=True, verbose_name='De totale geschatte netto taakduur van uw sessie komt op basis van uw opgave per taak uit op <strong>%d minuten</strong>. Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)')),
                ('tasks_stressful', models.NullBooleanField(default=False, verbose_name="Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.")),
                ('tasks_stressful_details', models.TextField(verbose_name='Waarom denkt u dat?', blank=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Naam')),
                ('minutes', models.PositiveIntegerField(verbose_name='Duur (in minuten)')),
                ('survey_url', models.URLField(verbose_name='URL', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=200, verbose_name='Wat is de naam van de taak?')),
                ('description', models.TextField(verbose_name='Wat is de beschrijving van de taak?')),
                ('duration', models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(45)])),
                ('registrations_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('feedback', models.BooleanField(default=False, verbose_name='Krijgt de proefpersoon tijdens of na deze taak feedback op zijn/haar gedrag of toestand?')),
                ('feedback_details', models.CharField(max_length=200, verbose_name='Beschrijf hoe de feedback wordt gegeven.', blank=True)),
                ('stressful', models.NullBooleanField(default=False, verbose_name="Is deze taak belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. En ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.")),
                ('stressful_details', models.TextField(verbose_name='Waarom denkt u dat?', blank=True)),
                ('registration_kind', models.ManyToManyField(to='proposals.RegistrationKind', verbose_name='Kies het soort meting:')),
                ('registrations', models.ManyToManyField(to='proposals.Registration', verbose_name='Hoe wordt het gedrag of de toestand van de proefpersoon bij deze taak vastgelegd?')),
                ('session', models.ForeignKey(to='proposals.Session')),
            ],
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('has_traits', models.BooleanField(default=False, verbose_name='Proefpersonen kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de proefpersonen het geval?')),
                ('traits_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('necessity', models.NullBooleanField(help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?', verbose_name='Is het om de onderzoeksvraag beantwoord te krijgen noodzakelijk om het geselecteerde type proefpersonen aan de studie te laten deelnemen?')),
                ('necessity_reason', models.TextField(verbose_name='Leg uit waarom', blank=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('risk_physical', models.NullBooleanField(default=False, verbose_name='Is de kans dat de proefpersoon fysieke schade oploopt tijdens het afnemen van de taak groter dan de kans op fysieke schade in het dagelijks leven?')),
                ('risk_psychological', models.NullBooleanField(default=False, verbose_name='Is de kans dat de proefpersoon psychische schade oploopt tijdens het afnemen van de taak groter dan de kans op psychische schade in het dagelijks leven?')),
                ('compensation_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('recruitment_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
                ('age_groups', models.ManyToManyField(to='proposals.AgeGroup', verbose_name='Geef hieronder aan binnen welke leeftijdscategorie uw proefpersonen vallen, er zijn meerdere antwoorden mogelijk')),
                ('compensation', models.ForeignKey(verbose_name='Welke vergoeding krijgt de proefpersoon voor zijn/haar deelname aan deze studie?', to='proposals.Compensation', help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld')),
                ('recruitment', models.ManyToManyField(to='proposals.Recruitment', verbose_name='Hoe worden de proefpersonen geworven?')),
                ('setting', models.ManyToManyField(to='proposals.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt')),
                ('traits', models.ManyToManyField(to='proposals.Trait', verbose_name='Selecteer de bijzondere kenmerken van uw proefpersonen', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wmo',
            fields=[
                ('metc', models.NullBooleanField(verbose_name='Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?')),
                ('metc_institution', models.CharField(max_length=200, verbose_name='Welke instelling?', blank=True)),
                ('is_medical', models.NullBooleanField(help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?')),
                ('is_behavioristic', models.NullBooleanField(help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.', verbose_name='Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?')),
                ('metc_application', models.BooleanField(default=False, verbose_name='Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?')),
                ('metc_decision', models.BooleanField(default=False, verbose_name='Is de METC al tot een beslissing gekomen?')),
                ('metc_decision_pdf', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de beslissing van het METC (in PDF-formaat)', validators=[proposals.models.validate_pdf])),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Geen beoordeling door METC noodzakelijk'), (1, 'In afwachting beslissing METC'), (2, 'Beslissing METC ge\xfcpload')])),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='proposal',
            field=models.ForeignKey(to='proposals.Proposal'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(related_name='applicants', verbose_name='Uitvoerende(n)', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='proposal',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(verbose_name='Te kopi\xebren aanvraag', to='proposals.Proposal', null=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='relation',
            field=models.ForeignKey(verbose_name='Wat is uw relatie tot het UiL OTS?', to='proposals.Relation'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='supervisor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', null=True, verbose_name='Eindverantwoordelijke onderzoeker'),
        ),
        migrations.AddField(
            model_name='survey',
            name='study',
            field=models.ForeignKey(to='proposals.Study'),
        ),
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([('proposal', 'order')]),
        ),
    ]
