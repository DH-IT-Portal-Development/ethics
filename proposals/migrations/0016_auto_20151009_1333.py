# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proposals', '0015_remove_proposal_supervisor_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='supervisor_email',
        ),
        migrations.AddField(
            model_name='proposal',
            name='supervisor',
            field=models.ForeignKey(verbose_name='Eindverantwoordelijke onderzoeker', to=settings.AUTH_USER_MODEL, help_text='Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.', null=True),
        ),
    ]
