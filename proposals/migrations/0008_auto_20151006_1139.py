# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0007_auto_20150821_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='sessions_number',
            field=models.PositiveIntegerField(help_text=b'Wanneer u bijvoorbeeld eerst de proefpersoon een taak/aantal taken laat doen tijdens een eerste bezoek aan het lab en u laat de proefpersoon nog een keer terugkomen om dezelfde taak/taken of andere taak/taken te doen, dan spreken we van twee sessies. Wanneer u meerdere taken afneemt op dezelfde dag, met pauzes daartussen, dan geldt dat toch als \xc3\xa9\xc3\xa9n sessie.', null=True, verbose_name=b'Hoeveel sessies telt deze studie?', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='supervisor_email',
            field=models.EmailField(help_text=b'Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', max_length=254, verbose_name=b'E-mailadres eindverantwoordelijke', blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='tasks_number',
            field=models.PositiveIntegerField(help_text=b'Wanneer u bijvoorbeeld eerst de proefpersoon observeert en de proefpersoon vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.', null=True, verbose_name=b'Hoeveel taken worden er binnen deze sessie bij de proefpersoon afgenomen?', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
