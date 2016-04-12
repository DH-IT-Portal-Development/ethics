# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.validators
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
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
            options={
                'ordering': ['order'],
            },
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
                ('needs_supervision', models.BooleanField(default=False)),
                ('requires_review', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('legally_incapable', models.BooleanField(verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wilsonbekwame deelnemers?')),
                ('has_traits', models.BooleanField(verbose_name='Deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?')),
                ('traits_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('necessity', models.NullBooleanField(help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen deelnemers te testen?', verbose_name='Is het, om de onderzoeksvraag beantwoord te krijgen, noodzakelijk om het geselecteerde type deelnemer aan de studie te laten meedoen?')),
                ('necessity_reason', models.TextField(verbose_name='Leg uit waarom', blank=True)),
                ('recruitment_details', models.CharField(max_length=200, verbose_name='Licht toe', blank=True)),
                ('setting_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('supervision', models.NullBooleanField(verbose_name='Vindt het afnemen van de taak plaats onder het toeziend oog van de leraar of een ander persoon die bevoegd is?')),
                ('compensation_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('has_observation', models.BooleanField(default=False, verbose_name='Observatieonderzoek')),
                ('has_intervention', models.BooleanField(default=False, verbose_name='Interventieonderzoek')),
                ('has_sessions', models.BooleanField(default=False, verbose_name='Taakonderzoek')),
                ('informed_consent', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc])),
                ('briefing', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc])),
                ('passive_consent', models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <link website?>', verbose_name='Maakt uw studie gebruik van passieve informed consent?')),
                ('sessions_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de deelnemer nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies telt deze studie?', validators=[django.core.validators.MinValueValidator(1)])),
                ('sessions_duration', models.PositiveIntegerField(help_text='Dit is de geschatte totale bruto tijd die de deelnemer kwijt is aan alle sessies bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name='De netto duur van uw studie komt op basis van uw opgegeven tijd, uit op <strong>%d minuten</strong>. Wat is de totale duur van de gehele studie? Schat de totale tijd die de deelnemers kwijt zijn aan de studie.')),
                ('stressful', models.NullBooleanField(help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", verbose_name='Is de studie op onderdelen of als geheel zodanig belastend dat deze <em>ondanks de verkregen informed consent </em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep, en neem ook de leeftijd van de deelnemers in deze inschatting mee.')),
                ('stressful_details', models.TextField(verbose_name='Licht je antwoord toe. Geef concrete voorbeelden van de relevante aspecten van uw studie (bijv. representatieve voorbeelden van mogelijk zeer kwetsende woorden of uitspraken in de taak, of van zeer confronterende vragen in een vragenlijst), zodat de commissie zich een goed beeld kan vormen.', blank=True)),
                ('risk', models.NullBooleanField(help_text='Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan de studie <em>meer dan</em> minimaal? minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"? Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie. En denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera.')),
                ('risk_details', models.TextField(max_length=200, verbose_name='Licht toe', blank=True)),
                ('age_groups', models.ManyToManyField(help_text='De beoogde leeftijdsgroep kan zijn 5-7 jarigen. Dan moet u hier hier 4-5 \xe9n 6-11 invullen', to='studies.AgeGroup', verbose_name='Geef aan binnen welke leeftijdscategorie(\xebn) uw deelnemersgroep valt')),
                ('compensation', models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname aan deze studie?', to='studies.Compensation', help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld')),
                ('proposal', models.ForeignKey(to='proposals.Proposal')),
                ('recruitment', models.ManyToManyField(to='studies.Recruitment', verbose_name='Hoe worden de deelnemers geworven?')),
                ('setting', models.ManyToManyField(to='studies.Setting', verbose_name='Geef aan waar de dataverzameling plaatsvindt')),
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
        migrations.AddField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='studies.Trait', verbose_name='Selecteer de bijzondere kenmerken van uw proefpersonen', blank=True),
        ),
    ]
