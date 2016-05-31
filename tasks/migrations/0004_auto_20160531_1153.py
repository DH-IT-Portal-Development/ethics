# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20160419_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(verbose_name='Beschrijf de taak die de deelnemer moet uitvoeren, en leg kort uit hoe deze taak (en de eventuele manipulaties daarbinnen) aan de beantwoording van uw onderzoeksvragen bijdraagt.'),
        ),
    ]
