# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0002_auto_20161013_1959"),
    ]

    operations = [
        migrations.AddField(
            model_name="study",
            name="passive_consent_details",
            field=models.TextField(
                verbose_name="Licht uw antwoord toe. Wij willen u wijzen op het reglement, sectie 3.1 'd' en 'e'. Passive consent is slechts in enkele gevallen toegestaan en draagt niet de voorkeur van de commissie.",
                blank=True,
            ),
        ),
    ]
