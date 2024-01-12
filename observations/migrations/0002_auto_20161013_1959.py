# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("observations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="description_en",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="registration",
            name="description_nl",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
