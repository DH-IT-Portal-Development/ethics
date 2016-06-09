# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0016_wmo_enforced_by_commission'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='pdf',
            field=models.FileField(upload_to=b'', blank=True),
        ),
    ]
