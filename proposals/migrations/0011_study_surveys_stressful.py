# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0010_recruitment_requires_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='surveys_stressful',
            field=models.NullBooleanField(default=False, verbose_name='Is het invullen van deze vragenlijsten belastend? Denk hierbij bijv. aan het type vragen dat gesteld wordt en aan de tijd die de persoon kwijt is met het invullen van alle vragenlijsten.'),
        ),
    ]
