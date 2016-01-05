# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='stressful',
        ),
        migrations.RemoveField(
            model_name='task',
            name='stressful_details',
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_stressful',
            field=models.NullBooleanField(default=False, verbose_name="Is het totaal van de sessie(s) als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep."),
        ),
        migrations.AlterField(
            model_name='task',
            name='registration_kind',
            field=models.ManyToManyField(to='proposals.RegistrationKind', verbose_name='Kies het soort meting:', blank=True),
        ),
    ]
