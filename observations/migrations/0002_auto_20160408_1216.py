# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='observation',
            old_name='is_test',
            new_name='is_in_target_group',
        ),
        migrations.AddField(
            model_name='observation',
            name='is_public_space',
            field=models.BooleanField(default=False, help_text='Bijvoorbeeld er wordt geobserveerd bij iemand thuis, tijdens een hypotheekgesprek of tijdens politieverhoren.', verbose_name='Wordt er geobserveerd in een niet-openbare ruimte?'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='is_anonymous',
            field=models.BooleanField(default=False, help_text='Zoals zou kunnen voorkomen op fora en de onderzoeker ook een account heeft.', verbose_name='Wordt er anoniem geobserveerd?'),
        ),
    ]
