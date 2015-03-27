# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20150327_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='creator_function',
            field=models.CharField(default=1, max_length=1, verbose_name=b'Functie', choices=[(1, b'(PhD) student'), (2, b'post-doc'), (3, b'UD'), (4, b'professor')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='applicants',
            field=models.ManyToManyField(related_name='applicants', verbose_name=b'Uitvoerende(n)', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
