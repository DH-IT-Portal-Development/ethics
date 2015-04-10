# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_auto_20150407_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Algemene informatie ingevuld'), (2, b'WMO: in afwachting beslissing'), (3, b'WMO: afgerond'), (4, b'Kenmerken studie toegevoegd'), (5, b'Belasting proefpersoon: taken toevoegen'), (6, b'Belasting proefpersoon: alle taken toegevoegd'), (7, b'Belasting proefpersoon: afgerond'), (8, b'Informed consent geupload'), (9, b'Opgestuurd')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='tasks_duration',
            field=models.PositiveIntegerField(null=True, verbose_name=b'De totale geschatte netto taakduur van Uw sessie komt op basis van uw opgave per taak uit op <strong>%d minuten</strong>. Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='tech_summary',
            field=models.TextField(verbose_name=b'Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over proefpersonen, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi\xc3\xabnten van de methode meer gedetailleerde informatie worden gevraagd.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(default=False, verbose_name=b'Proefpersonen kunnen geselecteerd worden op bepaalde bijzondere kenmerken die mogelijk samenhangen met een verhoogde kwetsbaarheid of verminderde belastbaarheid t.a.v. aspecten van de beoogde studie (bijvoorbeeld: kinderen die vroeger gepest zijn in een onderzoek naar de neurale reactie op verbale beledigingen; pati\xc3\xabnten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). Is dit in uw studie bij (een deel van) de proefpersonen het geval?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='setting',
            field=models.ForeignKey(verbose_name=b'Geef aan waar de dataverzameling plaatsvindt', to='proposals.Setting'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='proposals.Trait', verbose_name=b'Selecteer de bijzondere kenmerken van uw proefpersonen', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(verbose_name=b'Wat is de duur van deze taak van begin tot eind in minuten, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_application',
            field=models.BooleanField(default=False, verbose_name=b'Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is voor deze studie al een METC aanvraag ingediend?'),
            preserve_default=True,
        ),
    ]
