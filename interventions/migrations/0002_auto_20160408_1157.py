# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervention',
            name='is_supervised',
            field=models.BooleanField(default=False, verbose_name='Vindt de interventie plaats onder het toezicht van een een bevoegd persoon die, wanneer de interventie niet zou plaatsvinden, er ook zou zijn. Zoals een leraar of logopedist.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='intervention',
            name='description',
            field=models.TextField(verbose_name='Beschrijf de interventie(s). Geef aan waar de interventie plaatsvindt en binnen hoeveel sessies. Geef een duidelijke beschrijving van wat de interventie inhoud en welke partijen er bij betrokken zijn.'),
        ),
    ]
