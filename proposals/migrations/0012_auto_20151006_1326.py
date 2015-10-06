# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0011_auto_20151006_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='survey_file',
            field=models.FileField(default='', upload_to=b'', verbose_name='Bestand', blank=True),
            preserve_default=False,
        ),
    ]
