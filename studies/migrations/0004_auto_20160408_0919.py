# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0003_auto_20160401_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='compensation',
            field=models.ForeignKey(verbose_name='Welke vergoeding krijgt de deelnemer voor zijn/haar deelname aan deze studie?', to='studies.Compensation', help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld', null=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='has_traits',
            field=models.NullBooleanField(verbose_name='Deelnemers kunnen ge\xefncludeerd worden op bepaalde bijzondere kenmerken. Is dit in uw studie bij (een deel van) de deelnemers het geval?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.NullBooleanField(verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wilsonbekwame deelnemers?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='name',
            field=models.CharField(max_length=200, null=True, verbose_name='Wat is de naam van deze deelnemersgroep?'),
        ),
    ]
