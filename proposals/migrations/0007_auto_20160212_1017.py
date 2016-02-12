# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0006_auto_20160212_0822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='deception',
        ),
        migrations.RemoveField(
            model_name='session',
            name='deception_details',
        ),
        migrations.AddField(
            model_name='task',
            name='deception',
            field=models.BooleanField(default=False, help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen deze sessie sprake van misleiding van de deelnemer, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
        migrations.AddField(
            model_name='task',
            name='deception_details',
            field=models.TextField(verbose_name=b'Geef een toelichting en beschrijf hoe en wanneer de deelnemer zal worden gedebrieft.', blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='registration_kinds',
            field=models.ManyToManyField(to='proposals.RegistrationKind', verbose_name='Kies het soort meting', blank=True),
        ),
    ]
