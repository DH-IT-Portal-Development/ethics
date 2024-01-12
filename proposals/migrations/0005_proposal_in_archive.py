# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0004_auto_20161013_1508"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="in_archive",
            field=models.BooleanField(default=False),
        ),
    ]
