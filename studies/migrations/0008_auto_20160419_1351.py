# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0007_remove_study_sessions_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='deception',
            field=models.NullBooleanField(help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen bovenstaand onderzoekstraject sprake van misleiding van de deelnemer, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
        migrations.AddField(
            model_name='study',
            name='deception_details',
            field=models.TextField(verbose_name='Geef een toelichting en beschrijf hoe en wanneer de deelnemer zal worden gedebrieft.', blank=True),
        ),
    ]
