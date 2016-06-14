# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0022_agegroup_is_adult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='compensation',
            field=models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname?', to='studies.Compensation', help_text='Het standaardbedrag voor vergoeding aan de deelnemers is \u20ac10,- per uur. Minderjarigen mogen geen geld ontvangen, maar wel een cadeautje.', null=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.BooleanField(default=False, help_text='Wilsonbekwame volwassenen zijn volwassenen die waarvan redelijkerwijs mag worden aangenomen dat ze onvoldoende kunnen inschatten wat hun eventuele deelname allemaal behelst, en/of waarvan anderszins mag worden aangenomen dat informed consent niet goed gerealiseerd kan worden (bijvoorbeeld omdat ze niet goed hun eigen mening kunnen geven). Hier dient in ieder geval altijd informed consent van een relevante vertegenwoordiger te worden verkregen.', verbose_name='Maakt uw studie gebruik van wils<u>on</u>bekwame (volwassen) deelnemers?'),
        ),
    ]
