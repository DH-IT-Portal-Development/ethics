# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-04 08:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0014_auto_20180808_1129"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="has_minor_revision",
            field=models.BooleanField(
                default=False,
                verbose_name="Is er een revisie geweest na het indienen van deze studie?",
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="minor_revision_description",
            field=models.TextField(blank=True, null=True, verbose_name="Leg uit"),
        ),
    ]
