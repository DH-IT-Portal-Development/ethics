# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0019_auto_20160318_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='other_stakeholders',
            field=models.BooleanField(default=False, verbose_name='Zijn er onderzoekers van buiten UiL OTS bij deze studie betrokken?'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='stakeholders',
            field=models.TextField(verbose_name='Andere betrokkenen', blank=True),
        ),
    ]
