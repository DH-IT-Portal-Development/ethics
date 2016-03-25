# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import proposals.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0022_auto_20160319_1410'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compensation',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='funding',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='recruitment',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='registration',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='registrationkind',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='relation',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='setting',
            options={'ordering': ['order']},
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='date_end',
        ),
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, 'Algemene informatie ingevuld'), (2, 'WMO: geen beoordeling door METC noodzakelijk'), (3, 'WMO: wordt beoordeeld door METC'), (4, 'Kenmerken studie toegevoegd'), (5, 'Opzet studie: gestart'), (10, 'Nadere specificatie van het interventieonderdeel'), (20, 'Nadere specificatie van het observatieonderdeel'), (30, 'Nadere specificatie van het takenonderdeel'), (31, 'Takenonderdeel: taken toevoegen'), (32, 'Takenonderdeel: alle taken toegevoegd'), (33, 'Takenonderdeel: afgerond'), (34, 'Opzet studie: afgerond'), (40, 'Opgestuurd ter beoordeling door eindverantwoordelijke'), (50, 'Opgestuurd ter beoordeling door ETCL'), (55, 'Studie is beoordeeld door ETCL'), (60, 'Studie is beoordeeld door METC')]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='summary',
            field=models.TextField(verbose_name='Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.', validators=[proposals.validators.MaxWordsValidator(200)]),
        ),
        migrations.AlterField(
            model_name='study',
            name='recruitment_details',
            field=models.CharField(max_length=200, verbose_name='Licht toe', blank=True),
        ),
    ]
