# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_auto_20151006_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='registration',
            name='needs_kind',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='survey',
            name='survey_file',
            field=models.FileField(upload_to=b'', null=True, verbose_name='Bestand'),
        ),
        migrations.AddField(
            model_name='survey',
            name='survey_url',
            field=models.URLField(verbose_name='URL', blank=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='parent',
            field=models.ForeignKey(verbose_name='Te kopi\xebren aanvraag', to='proposals.Proposal', null=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_number',
            field=models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de proefpersoon een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de proefpersoon nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies telt deze studie?', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting proefpersoon: sessies toevoegen'), (6, 'Belasting proefpersoon: taken toevoegen'), (7, 'Belasting proefpersoon: alle taken toegevoegd'), (8, 'Belasting proefpersoon: afgerond'), (9, 'Belasting proefpersoon: afgerond'), (10, 'Informed consent ge\xfcpload'), (50, 'Opgestuurd ter beoordeling naar ETCL'), (55, 'Aanvraag is beoordeeld naar ETCL'), (60, 'Aanvraag is beoordeeld door METC')]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='tech_summary',
            field=models.TextField(verbose_name='Schrijf hier een samenvatting van 200-300 woorden, met daarin (a) een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen, en (b) een korte beschrijving van de beoogde methode, d.w.z. een mini-versie van de toekomstige Methode-sectie, met informatie over proefpersonen, materiaal (taken, stimuli), design, en procedure. Het gaat er hier vooral om dat de relatie tussen de onderzoeksvraag of -vragen en de beoogde methode voldoende helder is; verderop in deze aanmelding zal voor specifieke ingredi\xebnten van de methode meer gedetailleerde informatie worden gevraagd.'),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.BooleanField(default=False, verbose_name='Proefpersonen kunnen geselecteerd worden op bepaalde bijzondere kenmerken die mogelijk samenhangen met een verhoogde kwetsbaarheid of verminderde belastbaarheid t.a.v. aspecten van de beoogde studie (bijvoorbeeld: kinderen die vroeger gepest zijn in een onderzoek naar de neurale reactie op verbale beledigingen; pati\xebnten met afasie die een gesprek moeten voeren, ook al gaat het gesprek over alledaagse dingen). Is dit in uw studie bij (een deel van) de proefpersonen het geval?'),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Geen beoordeling door METC noodzakelijk'), (1, 'In afwachting beslissing METC'), (2, 'Beslissing METC ge\xfcpload')]),
        ),
        migrations.AddField(
            model_name='registrationkind',
            name='registration',
            field=models.ForeignKey(to='proposals.Registration'),
        ),
        migrations.AddField(
            model_name='task',
            name='registration_kind',
            field=models.ForeignKey(verbose_name='Namelijk', to='proposals.RegistrationKind', null=True),
        ),
    ]
