# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0005_auto_20150626_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='agegroup',
            name='needs_details',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Algemene informatie ingevuld'), (2, b'WMO: geen beoordeling door METC noodzakelijk'), (3, b'WMO: wordt beoordeeld door METC'), (4, b'Kenmerken studie toegevoegd'), (5, b'Belasting proefpersoon: sessies toevoegen'), (6, b'Belasting proefpersoon: taken toevoegen'), (7, b'Belasting proefpersoon: alle taken toegevoegd'), (8, b'Belasting proefpersoon: afgerond'), (9, b'Belasting proefpersoon: afgerond'), (10, b'Informed consent ge\xc3\xbcpload'), (50, b'Opgestuurd ter beoordeling naar ETCL'), (55, b'Aanvraag is beoordeeld naar ETCL'), (60, b'Aanvraag is beoordeeld door METC')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='minutes',
            field=models.PositiveIntegerField(verbose_name=b'Duur (in minuten)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='name',
            field=models.CharField(max_length=200, verbose_name=b'Naam'),
            preserve_default=True,
        ),
    ]
