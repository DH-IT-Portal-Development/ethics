# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='procedure',
        ),
        migrations.AddField(
            model_name='proposal',
            name='tasks_duration',
            field=models.PositiveIntegerField(null=True, verbose_name=b'De totale geschatte netto taakduur van Uw sessie komt op basis van uw opgave per taak uit op %d. Hoe lang duurt de totale sessie, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='tasks_number',
            field=models.PositiveIntegerField(help_text=b'Wanneer u bijvoorbeeld eerst de proefpersoon observeert en de proefpersoon vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name=b'Hoeveel taken worden er binnen deze studie bij de proefpersoon afgenomen?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='tasks_stressful',
            field=models.NullBooleanField(verbose_name=b'Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collegas, bij de proefpersonen zelf, bij derden)? Denk hierbij bijvoorbeeld aan de totale duur, vermoeidheid, etc. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de meest kwetsbare c.q. minst belastbare proefpersonengroep.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='actions_details',
            field=models.CharField(max_length=200, verbose_name=b'Namelijk', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='feedback',
            field=models.BooleanField(default=False, verbose_name=b'Krijgt de proefpersoon tijdens of na deze taak feedback op zijn/haar gedrag of toestand?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='feedback_details',
            field=models.CharField(max_length=200, verbose_name=b'Van welke aard is deze feedback?', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='stressful',
            field=models.NullBooleanField(default=False, verbose_name=b'Is deze taak belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collegas, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. En ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Algemene informatie ingevuld'), (2, b'In afwachting beslissing WMO'), (3, b'WMO-gedeelte afgerond'), (4, b'Kenmerken studie toegevoegd'), (5, b'Belasting proefpersoon toegevoegd'), (6, b'Informed consent geupload'), (7, b'Opgestuurd')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='supervisor_email',
            field=models.EmailField(help_text=b'Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=75, verbose_name=b'E-mailadres eindverantwoordelijke', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='tech_summary',
            field=models.TextField(verbose_name=b'Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over proefpersonen, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi&#235;nten van de methode meer gedetailleerde informatie worden gevraagd.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='title',
            field=models.CharField(help_text=b'Kies s.v.p. een titel die niet volledig identiek is aan die van eerder ingediende studies.', unique=True, max_length=200, verbose_name=b'Wat is de titel van uw studie?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='actions',
            field=models.ManyToManyField(to='proposals.Action', verbose_name=b'Wat vraag je bij deze taak de proefpersoon te doen?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(verbose_name=b'Wat is de duur van deze taak van begin tot eind, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=200, verbose_name=b'Wat is de naam of korte beschrijving van de taak? (geef alleen een naam als daarmee volledig duidelijk is waar het om gaat, bijv "lexicale decisietaak")'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='registrations',
            field=models.ManyToManyField(to='proposals.Registration', verbose_name=b'Hoe wordt het gedrag of de toestand van de proefpersoon bij deze taak vastgelegd?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc',
            field=models.NullBooleanField(verbose_name=b'Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?'),
            preserve_default=True,
        ),
    ]
