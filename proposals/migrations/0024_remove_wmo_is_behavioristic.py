# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-12-14 14:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0023_auto_20201203_0906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wmo',
            name='is_behavioristic',
        ),
    ]