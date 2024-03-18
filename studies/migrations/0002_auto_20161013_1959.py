# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="agegroup",
            name="description_en",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="agegroup",
            name="description_nl",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="compensation",
            name="description_en",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="compensation",
            name="description_nl",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="description_en",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="description_nl",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="trait",
            name="description_en",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="trait",
            name="description_nl",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
