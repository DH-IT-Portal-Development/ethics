# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0012_proposal_inform_local_staff"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="public",
            field=models.BooleanField(default=True),
        ),
    ]
