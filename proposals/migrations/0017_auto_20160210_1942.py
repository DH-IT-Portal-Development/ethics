# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0016_auto_20160209_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='sessions_duration',
            field=models.PositiveIntegerField(help_text='Dit is de geschatte totale bruto tijd die de deelnemer kwijt is aan alle sessie bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name='De totale geschatte nettoduur komt op basis van uw opgave per sessie uit op <strong>%d minuten</strong>. Wat is de totale duur van de studie? Dus hoeveel tijd zijn de deelnemers in totaal kwijt door mee te doen aan deze studie?'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_number',
            field=models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de deelnemer nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies telt deze studie?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting deelnemer: sessies toevoegen'), (6, 'Belasting deelnemer: taken toevoegen'), (7, 'Belasting deelnemer: alle taken toegevoegd'), (8, 'Belasting deelnemer: afgerond'), (9, 'Belasting deelnemer: afgerond'), (10, 'Informed consent ge\xfcpload'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Aanvraag is beoordeeld door ETCL'), (60, 'Aanvraag is beoordeeld door METC')]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='tech_summary',
            field=models.TextField(verbose_name='Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over deelnemers, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi\xebnten van de methode meer gedetailleerde informatie worden gevraagd.'),
        ),
        migrations.AlterField(
            model_name='session',
            name='deception',
            field=models.NullBooleanField(help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen deze sessie sprake van misleiding van de deelnemer, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
        migrations.AlterField(
            model_name='session',
            name='deception_details',
            field=models.TextField(verbose_name=b'Geef een toelichting en beschrijf hoe en wanneer de deelnemer zal worden gedebrieft.', blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='tasks_number',
            field=models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer observeert en de deelnemer vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name='Hoeveel taken worden er binnen deze sessie bij de deelnemer afgenomen?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='study',
            name='age_groups',
            field=models.ManyToManyField(to='proposals.AgeGroup', verbose_name='Geef aan binnen welke leeftijdscategorie uw deelnemers vallen, er zijn meerdere antwoorden mogelijk'),
        ),
        migrations.AlterField(
            model_name='study',
            name='compensation',
            field=models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname aan deze studie?', to='proposals.Compensation', help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld'),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(default=False, verbose_name='deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.BooleanField(default=False, verbose_name=' Maakt uw studie gebruik van wilsonbekwame deelnemers?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='necessity',
            field=models.NullBooleanField(help_text='Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou u de vraag ook kunnen beantwoorden door volwassen deelnemers te testen?', verbose_name='Is het om de onderzoeksvraag beantwoord te krijgen noodzakelijk om het geselecteerde type deelnemers aan de studie te laten deelnemen?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='recruitment',
            field=models.ManyToManyField(to='proposals.Recruitment', verbose_name='Hoe worden de deelnemers geworven?'),
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(45)]),
        ),
        migrations.AlterField(
            model_name='task',
            name='feedback',
            field=models.BooleanField(default=False, verbose_name='Krijgt de deelnemer tijdens of na deze taak feedback op zijn/haar gedrag of toestand?'),
        ),
        migrations.AlterField(
            model_name='task',
            name='registrations',
            field=models.ManyToManyField(to='proposals.Registration', verbose_name='Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?'),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='is_behavioristic',
            field=models.NullBooleanField(help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken.', verbose_name='Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?'),
        ),
    ]
