# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('go', models.NullBooleanField(default=None, verbose_name='Beslissing')),
                ('date_decision', models.DateTimeField(null=True, blank=True)),
                ('comments', models.TextField(verbose_name='Ruimte voor eventuele opmerkingen', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stage', models.PositiveIntegerField(default=0, choices=[(0, 'Beoordeling door supervisor'), (1, 'Aanstelling commissieleden'), (2, 'Beoordeling door ethische commissie')])),
                ('go', models.NullBooleanField(default=None, verbose_name='Beslissing')),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField(null=True, blank=True)),
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
        migrations.AlterUniqueTogether(
            name='decision',
            unique_together=set([('review', 'reviewer')]),
        ),
    ]
