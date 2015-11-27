# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0019_auto_20151113_2146'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Meeting',
        ),
        migrations.DeleteModel(
            name='Member',
        ),
        migrations.AlterField(
            model_name='proposal',
            name='supervisor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', null=True, verbose_name='Eindverantwoordelijke onderzoeker'),
        ),
    ]
