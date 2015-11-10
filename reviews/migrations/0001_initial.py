# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0014_auto_20151009_1327'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('go', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('go', models.NullBooleanField()),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField(null=True)),
                ('proposal', models.ForeignKey(to='proposals.Proposal')),
            ],
        ),
        migrations.AddField(
            model_name='decision',
            name='review',
            field=models.ForeignKey(to='reviews.Review'),
        ),
        migrations.AddField(
            model_name='decision',
            name='reviewer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
