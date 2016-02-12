# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0007_auto_20160212_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationkind',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
    ]
