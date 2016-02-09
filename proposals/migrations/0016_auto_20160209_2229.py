# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0015_auto_20160209_2216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='sessions_stressful',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='sessions_stressful_details',
        ),
        migrations.RemoveField(
            model_name='session',
            name='stressful',
        ),
        migrations.RemoveField(
            model_name='session',
            name='stressful_details',
        ),
        migrations.RemoveField(
            model_name='session',
            name='tasks_stressful',
        ),
        migrations.RemoveField(
            model_name='session',
            name='tasks_stressful_details',
        ),
        migrations.AddField(
            model_name='study',
            name='stressful',
            field=models.NullBooleanField(default=False, help_text="Dit zou bijvoorbeeld het geval kunnen zijn bij een 'onmenselijk' lange en uitputtende taak, een zeer confronterende vragenlijst, of voortdurend vernietigende feedback, maar ook bij een ervaren inbreuk op de  privacy, of een ander ervaren gebrek aan respect.", verbose_name='Is de studie op onderdelen of als geheel zodanig belastend dat deze ondanks de verkregen informed consent vragen zou kunnen oproepen (of zelfs verontwaardiging), bijvoorbeeld bij collega-onderzoekers, bij de deelnemers zelf, of bij ouders of andere vertegenwoordigers? Ga bij het beantwoorden van deze vraag uit van de volgens u meest kwetsbare c.q. minst belastbare deelnemersgroep.'),
        ),
        migrations.AddField(
            model_name='study',
            name='stressful_details',
            field=models.TextField(verbose_name='Licht toe', blank=True),
        ),
    ]
