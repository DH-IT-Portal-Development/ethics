# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0024_funding_requires_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrationkind',
            name='registration',
        ),
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='session',
            name='study',
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='task',
            name='registration_kinds',
        ),
        migrations.RemoveField(
            model_name='task',
            name='registrations',
        ),
        migrations.RemoveField(
            model_name='task',
            name='session',
        ),
        migrations.DeleteModel(
            name='Registration',
        ),
        migrations.DeleteModel(
            name='RegistrationKind',
        ),
        migrations.DeleteModel(
            name='Session',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
