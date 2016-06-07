# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0015_proposal_status_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='wmo',
            name='enforced_by_commission',
            field=models.BooleanField(default=False),
        ),
    ]
