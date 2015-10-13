# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0017_auto_20151011_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting proefpersoon: sessies toevoegen'), (6, 'Belasting proefpersoon: taken toevoegen'), (7, 'Belasting proefpersoon: alle taken toegevoegd'), (8, 'Belasting proefpersoon: afgerond'), (9, 'Belasting proefpersoon: afgerond'), (10, 'Informed consent ge\xfcpload'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Aanvraag is beoordeeld door ETCL'), (60, 'Aanvraag is beoordeeld door METC')]),
        ),
    ]
