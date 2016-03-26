# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0025_auto_20160325_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(unique=True)),
                ('description', models.CharField(max_length=200)),
                ('needs_details', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='study',
            name='traits_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.AddField(
            model_name='study',
            name='traits',
            field=models.ManyToManyField(to='proposals.Trait', verbose_name='Selecteer de bijzondere kenmerken van uw proefpersonen', blank=True),
        ),
    ]
