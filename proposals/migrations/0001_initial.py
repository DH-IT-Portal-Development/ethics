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
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_number', models.CharField(unique=True, max_length=16)),
                ('date_start', models.DateField(verbose_name='Wat is de beoogde startdatum van uw studie?')),
                ('date_end', models.DateField(verbose_name='Wat is de beoogde einddatum van uw studie?')),
                ('title', models.CharField(help_text='Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', unique=True, max_length=200, verbose_name='Wat is de titel van uw studie?')),
                ('tech_summary', models.TextField(verbose_name='Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over deelnemers, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi\xebnten van de methode meer gedetailleerde informatie worden gevraagd.')),
                ('other_applicants', models.BooleanField(default=False, verbose_name='Zijn er nog andere UiL OTS-onderzoekers bij deze studie betrokken?')),
                ('comments', models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True)),
                ('allow_in_archive', models.BooleanField(default=True, help_text='Dit archief is alleen toegankelijk voor mensen die aan het UiL OTS geaffilieerd zijn.', verbose_name='Mag deze aanvraag ter goedkeuring in het semi-publiekelijk archief?')),
                ('informed_consent_pdf', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de toestemmingsverklaring (in PDF-formaat)', validators=[proposals.models.validate_pdf_or_doc])),
                ('briefing_pdf', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief (in PDF-formaat)', validators=[proposals.models.validate_pdf_or_doc])),
                ('passive_consent', models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <link website?>', verbose_name='Maakt uw studie gebruik van passieve informed consent?')),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting deelnemer: sessies toevoegen'), (6, 'Belasting deelnemer: taken toevoegen'), (7, 'Belasting deelnemer: alle taken toegevoegd'), (8, 'Belasting deelnemer: afgerond'), (9, 'Belasting deelnemer: afgerond'), (10, 'Informed consent ge\xfcpload'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Aanvraag is beoordeeld door ETCL'), (60, 'Aanvraag is beoordeeld door METC')])),
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
                ('requires_review', models.BooleanField(default=False)),
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
                ('age_min', models.PositiveIntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
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
                ('deception', models.NullBooleanField(help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen deze sessie sprake van misleiding van de deelnemer, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.')),
                ('deception_details', models.TextField(verbose_name=b'Geef een toelichting en beschrijf hoe en wanneer de deelnemer zal worden gedebrieft.', blank=True)),
                ('tasks_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer observeert en de deelnemer vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name='Hoeveel taken worden er binnen deze sessie bij de deelnemer afgenomen?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('tasks_duration', models.PositiveIntegerField(null=True, verbose_name='De totale geschatte netto taakduur van uw sessie komt op basis van uw opgave per taak uit op <strong>%d minuten</strong>. Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)')),
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
                ('name', models.CharField(max_length=200, verbose_name='Naam vragenlijst')),
                ('minutes', models.PositiveIntegerField(verbose_name='Duur (in minuten)')),
                ('survey_url', models.URLField(verbose_name='URL', blank=True)),
                ('description', models.TextField(verbose_name='Korte beschrijving')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=200, verbose_name='Wat is de naam van de taak?')),
                ('description', models.TextField(verbose_name='Wat is de beschrijving van de taak?')),
                ('duration', models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1)])),
                ('registrations_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('registration_kinds_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('feedback', models.BooleanField(default=False, verbose_name='Krijgt de deelnemer tijdens of na deze taak feedback op zijn/haar gedrag of toestand?')),
                ('feedback_details', models.CharField(max_length=200, verbose_name='Beschrijf hoe de feedback wordt gegeven.', blank=True)),
                ('registration_kinds', models.ManyToManyField(to='proposals.RegistrationKind', verbose_name='Kies het soort meting:', blank=True)),
                ('registrations', models.ManyToManyField(to='proposals.Registration', verbose_name='Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?')),
                ('session', models.ForeignKey(to='proposals.Session')),
            ],
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('legally_incapable', models.BooleanField(default=False, verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wilsonbekwame deelnemers?')),
                ('has_traits', models.BooleanField(default=False, verbose_name='Deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?')),
                ('necessity', models.NullBooleanField(help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen deelnemers te testen?', verbose_name='Is het, om de onderzoeksvraag beantwoord te krijgen, noodzakelijk om het geselecteerde type deelnemer aan de studie te laten meedoen?')),
                ('necessity_reason', models.TextField(verbose_name='Leg uit waarom', blank=True)),
                ('recruitment_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('compensation_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('stressful', models.NullBooleanField(default=False, help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de  privacy, of een ander ervaren gebrek aan respect.", verbose_name='Is de studie op onderdelen of als geheel zodanig belastend dat deze ondanks de verkregen informed consent vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep.')),
                ('stressful_details', models.TextField(verbose_name='Licht toe', blank=True)),
                ('risk', models.NullBooleanField(default=False, help_text=b"Denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, et cetera. Het achtergrondrisico omvat ook de risico's van 'routine'-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-assessment, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles waar relevant onder begeleiding van adequaat geschoolde specialisten).", verbose_name='Zijn de risico\'s van deelname aan de studie meer dan minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke fysieke of psychische schade bij de deelnemers duidelijk boven het "achtergrondrisico", datgene dat gezonde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie, maar bepaal het achtergrondrisico op basis van de gemiddelde bevolking.')),
                ('risk_details', models.CharField(max_length=200, verbose_name='Licht toe', blank=True)),
                ('sessions_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de deelnemer nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies telt deze studie?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('sessions_duration', models.PositiveIntegerField(help_text='Dit is de geschatte totale bruto tijd die de deelnemer kwijt is aan alle sessies bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name='De netto duur van uw studie komt op basis van uw opgegeven tijd, uit op <strong>%d minuten</strong>. Wat is de totale duur van de gehele studie? Schat de totale tijd die de deelnemers kwijt zijn aan de studie.')),
                ('surveys_stressful', models.NullBooleanField(default=False, verbose_name='Is het invullen van deze vragenlijsten belastend? Denk hierbij bijv. aan het type vragen dat gesteld wordt en aan de tijd die de persoon kwijt is met het invullen van alle vragenlijsten.')),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
                ('age_groups', models.ManyToManyField(to='proposals.AgeGroup', verbose_name='Geef aan binnen welke leeftijdscategorie uw deelnemers vallen, er zijn meerdere antwoorden mogelijk')),
                ('compensation', models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname aan deze studie?', to='proposals.Compensation', help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld')),
                ('recruitment', models.ManyToManyField(to='proposals.Recruitment', verbose_name='Hoe worden de deelnemers geworven?')),
                ('setting', models.ManyToManyField(to='proposals.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt')),
            ],
        ),
        migrations.CreateModel(
            name='Wmo',
            fields=[
                ('metc', models.NullBooleanField(verbose_name='Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?')),
                ('metc_institution', models.CharField(max_length=200, verbose_name='Welke instelling?', blank=True)),
                ('is_medical', models.NullBooleanField(help_text='De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)', verbose_name='Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?')),
                ('is_behavioristic', models.NullBooleanField(help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken.', verbose_name='Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?')),
                ('metc_application', models.BooleanField(default=False, verbose_name='Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?')),
                ('metc_decision', models.BooleanField(default=False, verbose_name='Is de METC al tot een beslissing gekomen?')),
                ('metc_decision_pdf', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de beslissing van het METC (in PDF-formaat)', validators=[proposals.models.validate_pdf_or_doc])),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Geen beoordeling door METC noodzakelijk'), (1, 'In afwachting beslissing METC'), (2, 'Beslissing METC ge\xfcpload')])),
                ('proposal', models.OneToOneField(primary_key=True, serialize=False, to='proposals.Proposal')),
            ],
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
            field=models.ForeignKey(verbose_name='Te kopi\xebren aanvraag', to='proposals.Proposal', help_text='Dit veld toont enkel aanvragen waar u zelf een medeaanvrager bent.', null=True),
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
        migrations.AddField(
            model_name='session',
            name='study',
            field=models.ForeignKey(to='proposals.Study'),
        ),
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([('study', 'order')]),
        ),
    ]
