# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0002_auto_20160408_1216'),
    ]

    operations = [
        migrations.RenameField(
            model_name='observation',
            old_name='is_public_space',
            new_name='is_nonpublic_space',
        ),
        migrations.AddField(
            model_name='observation',
            name='has_advanced_consent',
            field=models.BooleanField(default=True, verbose_name='Vindt de informed consent van tevoren plaats?'),
        ),
    ]
