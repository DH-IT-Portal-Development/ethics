# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-26 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0020_auto_20190401_1348"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="reference_number",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
