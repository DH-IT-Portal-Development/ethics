# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Faq",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("order", models.PositiveIntegerField(unique=True)),
                ("question", models.TextField()),
                ("answer", models.TextField()),
            ],
            options={
                "verbose_name": "FAQ",
            },
        ),
    ]
