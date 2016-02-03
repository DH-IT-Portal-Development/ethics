# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0013_auto_20160203_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='passive_consent',
            field=models.BooleanField(default=False, verbose_name='Maakt uw studie gebruik van passieve informed consent?'),
        ),
    ]
