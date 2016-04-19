# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0009_auto_20160419_1414'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Setting',
        ),
        migrations.AlterModelOptions(
            name='trait',
            options={'ordering': ['order']},
        ),
        migrations.RemoveField(
            model_name='study',
            name='setting',
        ),
    ]
