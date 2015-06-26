# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0004_auto_20150612_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='wmo',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Geen beoordeling door METC noodzakelijk'), (1, b'In afwachting beslissing METC'), (2, b'Beslissing METC ge\xc3\xbcpload')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='sessions_duration',
            field=models.PositiveIntegerField(help_text=b'Dit is de geschatte totale bruto tijd die de proefpersoon kwijt is aan alle sessie bij elkaar opgeteld, exclusief reistijd.', null=True, verbose_name=b'De totale geschatte netto studieduur van uw sessie komt op basis van uw opgave per sessie uit op <strong>%d minuten</strong>. Schat de totale tijd die uw proefpersonen aan de gehele studie zullen besteden.'),
            preserve_default=True,
        ),
    ]
