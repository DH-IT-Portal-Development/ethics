# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0003_study_passive_consent_details"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recruitment",
            options={"ordering": ["order"], "verbose_name": "Werving"},
        ),
        migrations.AddField(
            model_name="recruitment",
            name="is_local",
            field=models.BooleanField(default=False),
        ),
    ]
