# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0004_auto_20160408_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='age_groups',
            field=models.ManyToManyField(help_text='De beoogde leeftijdsgroep kan zijn 5-7 jarigen. Dan moet u hier hier 4-5 \xe9n 6-11 invullen', to='studies.AgeGroup', verbose_name='Uit welke leeftijdscategorie(\xebn) bestaat uw deelnemersgroep?'),
        ),
        migrations.AlterField(
            model_name='study',
            name='legally_incapable',
            field=models.NullBooleanField(verbose_name='Maakt uw studie gebruik van <strong>volwassen</strong> wils<u>on</u>bekwame deelnemers?'),
        ),
    ]
