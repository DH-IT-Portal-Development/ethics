# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0009_auto_20160528_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='is_nonpublic_space',
            field=models.BooleanField(default=False, help_text='Bijvoorbeeld er wordt geobserveerd bij iemand thuis, tijdens een hypotheekgesprek, tijdens politieverhoren of een forum waar een account voor moet worden aangemaakt.', verbose_name='Wordt er geobserveerd in een niet-openbare ruimte?'),
        ),
    ]
