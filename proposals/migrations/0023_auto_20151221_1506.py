# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import proposals.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0022_remove_survey_survey_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.TextField(default='', verbose_name='Wat is de beschrijving van de taak?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='informed_consent_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informed consent (in PDF-formaat)', validators=[proposals.models.validate_pdf]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_stressful',
            field=models.NullBooleanField(default=False, verbose_name="Is het totaal van sessies als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep."),
        ),
        migrations.AlterField(
            model_name='session',
            name='stressful',
            field=models.NullBooleanField(verbose_name="Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij bijvoorbeeld aan de totale duur, vermoeidheid, etc. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de meest kwetsbare c.q. minst belastbare proefpersonengroep."),
        ),
        migrations.AlterField(
            model_name='session',
            name='tasks_stressful',
            field=models.NullBooleanField(default=False, verbose_name="Is het geheel van taken en overige activiteiten in de sessie als geheel belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. Ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep."),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Wat is de naam van de taak?'),
        ),
        migrations.RemoveField(
            model_name='task',
            name='registration_kind',
        ),
        migrations.AddField(
            model_name='task',
            name='registration_kind',
            field=models.ManyToManyField(to='proposals.RegistrationKind', verbose_name='Kies het soort meting:'),
        ),
        migrations.AlterField(
            model_name='task',
            name='stressful',
            field=models.NullBooleanField(default=False, verbose_name="Is deze taak belastend voor de proefpersoon op een manier die, ondanks de verkregen informed consent, vragen zou kunnen oproepen (bijvoorbeeld bij collega's, bij de proefpersonen zelf, bij derden)? Denk hierbij aan zaken als de aard van de stimuli, de taakduur, saaiheid of (mentale/fysieke) veeleisendheid van de taak, de mate waarin proefpersonen zich ongemakkelijk kunnen voelen bij het geven van bepaalde antwoorden (bijv. depressievragenlijst) of bepaald gedrag, etcetera. En ga bij het beantwoorden van de vraag uit van wat u als onderzoeker beschouwt als de voor deze taak meest kwetsbare c.q. minst belastbare proefpersonengroep."),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_decision_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de beslissing van het METC (in PDF-formaat)', validators=[proposals.models.validate_pdf]),
        ),
    ]
