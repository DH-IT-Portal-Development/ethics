# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="is_revision",
            field=models.BooleanField(
                default=False,
                verbose_name="Is deze studie een revisie van of amendement op een ingediende studie?",
            ),
        ),
    ]
