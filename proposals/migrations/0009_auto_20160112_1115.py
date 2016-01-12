# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_auto_20160112_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='deception',
            field=models.NullBooleanField(verbose_name='Is er binnen deze sessie sprake van misleiding van de proefpersoon, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere proefpersonen wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
        migrations.AddField(
            model_name='session',
            name='deception_details',
            field=models.TextField(verbose_name=b'Geef een toelichting en beschrijf hoe en wanneer de proefpersoon zal worden gedebrieft.', blank=True),
        ),
    ]
