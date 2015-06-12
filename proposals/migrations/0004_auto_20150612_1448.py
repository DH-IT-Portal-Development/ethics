# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20150602_0955'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ['order']},
        ),
    ]
