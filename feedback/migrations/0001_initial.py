# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('comment', models.TextField(verbose_name=b'Opmerking')),
                ('priority', models.IntegerField(default=1, choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])),
                ('status', models.IntegerField(default=1, choices=[(1, 'Open'), (2, 'Working'), (3, 'Closed')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('submitter', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
