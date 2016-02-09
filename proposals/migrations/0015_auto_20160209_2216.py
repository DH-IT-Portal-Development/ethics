# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0014_proposal_passive_consent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='study',
            name='risk_physical',
        ),
        migrations.RemoveField(
            model_name='study',
            name='risk_psychological',
        ),
        migrations.AddField(
            model_name='study',
            name='risk',
            field=models.NullBooleanField(default=False, help_text=b"Denk bij schade ook aan de gevolgen die het voor de deelnemer of anderen beschikbaar komen van bepaalde informatie kan hebben, bijv. op het vlak van zelfbeeld, stigmatisering door anderen, et cetera. Het achtergrondrisico omvat ook de risico's van 'routine'-tests, -onderzoeken of -procedures die in alledaagse didactische, psychologische of medische contexten plaatsvinden (zoals een eindexamen, een rijexamen, een stressbestendigheids-assessment, een intelligentie- of persoonlijkheidstest, of een hartslagmeting na fysieke inspanning; dit alles waar relevant onder begeleiding van adequaat geschoolde specialisten).", verbose_name='Zijn de risico\'s van deelname aan de studie meer dan minimaal? D.w.z. ligt de kans op en/of omvang van mogelijke fysieke of psychische schade bij de deelnemers duidelijk boven het "achtergrondrisico", datgene dat gezonde burgers in de relevante leeftijdscategorie normaalgesproken in het dagelijks leven ten deel valt? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep in uw studie, maar bepaal het achtergrondrisico op basis van de gemiddelde bevolking.'),
        ),
        migrations.AddField(
            model_name='study',
            name='risk_details',
            field=models.CharField(max_length=200, verbose_name='Licht toe', blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='deception',
            field=models.NullBooleanField(help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen deze sessie sprake van misleiding van de proefpersoon, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere proefpersonen wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
    ]
