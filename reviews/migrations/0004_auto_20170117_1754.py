# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0003_decision_go_char"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="short_route",
            field=models.NullBooleanField(default=None, verbose_name="Route"),
        ),
    ]
