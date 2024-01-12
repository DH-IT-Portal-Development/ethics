# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-15 11:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0008_alter_user_username_max_length"),
        ("proposals", "0016_auto_20181005_1011"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="reviewing_committee",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="auth.Group",
                verbose_name="Door welke comissie dient deze studie te worden beoordeeld?",
            ),
            preserve_default=False,
        ),
    ]
