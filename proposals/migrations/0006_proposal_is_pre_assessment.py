# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0005_proposal_in_archive"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="is_pre_assessment",
            field=models.BooleanField(default=False),
        ),
    ]
