# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0005_auto_20160419_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='sessions_number',
            field=models.PositiveIntegerField(help_text='Wanneer u bijvoorbeeld eerst de deelnemer een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de deelnemer nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xe9\xe9n sessie.', null=True, verbose_name='Hoeveel sessies met taakonderzoek zullen de deelnemers doorlopen?', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
