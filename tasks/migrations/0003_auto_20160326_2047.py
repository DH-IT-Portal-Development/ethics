# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20160326_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deception',
            field=models.NullBooleanField(help_text='Wellicht ten overvloede: het gaat hierbij niet om fillers.', verbose_name='Is er binnen deze sessie sprake van misleiding van de deelnemer, d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of belangrijke aspecten van de gang van zaken tijdens de studie? Denk aan zaken als een bewust misleidende "cover story" voor het experiment; het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        ),
    ]
