# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0013_auto_20160312_2248'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='tech_summary',
        ),
        migrations.AddField(
            model_name='proposal',
            name='summary',
            field=models.TextField(default='', verbose_name='Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Belasting deelnemer: sessies toevoegen'), (6, 'Belasting deelnemer: taken toevoegen'), (7, 'Belasting deelnemer: alle taken toegevoegd'), (8, 'Belasting deelnemer: afgerond'), (9, 'Belasting deelnemer: afgerond'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Studie is beoordeeld door ETCL'), (60, 'Studie is beoordeeld door METC')]),
        ),
    ]
