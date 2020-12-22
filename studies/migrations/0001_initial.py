# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import main.validators
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
                ('is_adult', models.BooleanField(default=False)),
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
            name='Study',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=15, verbose_name='Naam traject', blank=True)),
                ('legally_incapable', models.BooleanField(default=False, help_text='Wilsonbekwame volwassenen zijn volwassenen die waarvan redelijkerwijs mag worden aangenomen dat ze onvoldoende kunnen inschatten wat hun eventuele deelname allemaal behelst, en/of waarvan anderszins mag worden aangenomen dat informed consent niet goed gerealiseerd kan worden (bijvoorbeeld omdat ze niet goed hun eigen mening kunnen geven). Hier dient in ieder geval altijd informed consent van een relevante vertegenwoordiger te worden verkregen.', verbose_name='Maakt uw studie gebruik van wils<u>on</u>bekwame (volwassen) deelnemers?')),
                ('legally_incapable_details', models.TextField(verbose_name='Licht toe', blank=True)),
                ('has_traits', models.NullBooleanField(verbose_name='Deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?')),
                ('traits_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('necessity', models.CharField(blank=True, help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen deelnemers te testen?', max_length=1, verbose_name='Is het, om de onderzoeksvraag beantwoord te krijgen, noodzakelijk om het geselecteerde type deelnemer aan de studie te laten meedoen?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')])),
                ('necessity_reason', models.TextField(verbose_name='Leg uit waarom', blank=True)),
                ('recruitment_details', models.TextField(verbose_name='Licht toe', blank=True)),
                ('compensation_details', models.CharField(max_length=200, verbose_name='Namelijk', blank=True)),
                ('has_intervention', models.BooleanField(default=False, verbose_name='Interventieonderzoek')),
                ('has_observation', models.BooleanField(default=False, verbose_name='Observatieonderzoek')),
                ('has_sessions', models.BooleanField(default=False, verbose_name='Taakonderzoek')),
                ('informed_consent', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)', validators=[main.validators.validate_pdf_or_doc])),
                ('briefing', models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief (in .pdf of .doc(x)-formaat)', validators=[main.validators.validate_pdf_or_doc])),
                ('passive_consent', models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <a href="https://etcl.wp.hum.uu.nl/toestemmingsverklaringen/" target="_blank">de ETCL-website</a>.', verbose_name='Maakt u gebruik van passieve informed consent?')),
                ('sessions_number', models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de deelnemer nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies met taakonderzoek zullen de deelnemers doorlopen?', validators=[django.core.validators.MinValueValidator(1)])),
                ('deception', models.CharField(blank=True, help_text='Misleiding is het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie. Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback. Wellicht ten overvloede: het gaat hierbij niet om fillers.', max_length=1, verbose_name='Is er binnen bovenstaand onderzoekstraject sprake van misleiding van de deelnemer?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')])),
                ('deception_details', models.TextField(verbose_name='Geef een toelichting en beschrijf hoe en wanneer de deelnemer zal worden gedebrieft.', blank=True)),
                ('negativity', models.CharField(blank=True, max_length=1, verbose_name='Bevat bovenstaand onderzoekstraject elementen die <em>tijdens</em> de deelname niet-triviale negatieve emoties kunnen opwekken? Denk hierbij bijvoorbeeld aan emotioneel indringende vragen, kwetsende uitspraken, negatieve feedback, frustrerende, zware, (heel) lange en/of (heel) saaie taken.', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')])),
                ('negativity_details', models.TextField(verbose_name='Licht uw antwoord toe.', blank=True)),
                ('stressful', models.CharField(blank=True, help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de privacy, of een ander ervaren gebrek aan respect. Let op, het gaat bij deze vraag om de door de deelnemer ervaren belasting tijdens het onderzoek, niet om de opgelopen psychische of fysieke schade door het onderzoek.", max_length=1, verbose_name='Bevat bovenstaand onderzoekstraject elementen die tijdens de deelname zodanig belastend zijn dat deze <em>ondanks de verkregen informed consent</em> vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')])),
                ('stressful_details', models.TextField(verbose_name='Licht uw antwoord toe. Geef concrete voorbeelden van de relevante aspecten van uw studie (bijv. representatieve voorbeelden van mogelijk zeer kwetsende woorden of uitspraken in de taak, of van zeer confronterende vragen in een vragenlijst), zodat de commissie zich een goed beeld kan vormen.', blank=True)),
                ('risk', models.CharField(blank=True, help_text='Achtergrondrisico is datgene dat gezonde, gemiddelde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt. Denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, economische schade door data-koppeling, et cetera. Het achtergrondrisico voor psychische en fysieke schade omvat bijvoorbeeld ook de risico\'s van "routine"-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-<em>assessment</em>, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles, waar relevant, onder begeleiding van adequaat geschoolde specialisten).', max_length=1, verbose_name='Zijn de risico\'s op psychische, fysieke, of andere (bijv. economische, juridische) schade door deelname aan bovenstaand onderzoekstraject <em>meer dan</em> minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke schade bij de deelnemers duidelijk <em>boven</em> het "achtergrondrisico"?', choices=[(b'Y', 'ja'), (b'N', 'nee'), (b'?', 'twijfel')])),
                ('risk_details', models.TextField(max_length=200, verbose_name='Licht toe', blank=True)),
                ('age_groups', models.ManyToManyField(help_text='De beoogde leeftijdsgroep kan zijn 5-7 jarigen. Dan moet u hier hier 4-5 \xe9n 6-11 invullen.', to='studies.AgeGroup', verbose_name='Uit welke leeftijdscategorie(\xebn) bestaat uw deelnemersgroep?')),
                ('compensation', models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname?', to='studies.Compensation', help_text='Het standaardbedrag voor vergoeding aan de deelnemers is \u20ac10,- per uur. Minderjarigen mogen geen geld ontvangen, maar wel een cadeautje.', null=True, on_delete=models.CASCADE)),
                ('proposal', models.ForeignKey(to='proposals.Proposal', on_delete=models.CASCADE)),
                ('recruitment', models.ManyToManyField(to='studies.Recruitment', verbose_name='Hoe worden de deelnemers geworven?')),
            ],
            options={
                'ordering': ['order'],
            },
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
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='studies.Trait', verbose_name='Selecteer de bijzondere kenmerken van uw proefpersonen', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='study',
            unique_together=set([('proposal', 'order')]),
        ),
    ]
