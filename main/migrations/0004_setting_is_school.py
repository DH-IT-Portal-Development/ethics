# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-08 12:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_auto_20170601_0816"),
    ]

    operations = [
        migrations.AddField(
            model_name="setting",
            name="is_school",
            field=models.BooleanField(default=False),
        ),
    ]
