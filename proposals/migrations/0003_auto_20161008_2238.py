# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0002_proposal_is_revision"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="in_course",
            field=models.BooleanField(
                default=False,
                verbose_name="Ik vul deze portal in in de context van een cursus",
            ),
        ),
        migrations.AddField(
            model_name="relation",
            name="check_in_course",
            field=models.BooleanField(default=True),
        ),
    ]
