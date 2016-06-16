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
                ('stage', models.PositiveIntegerField(default=0, choices=[(0, 'Beoordeling door eindverantwoordelijke'), (1, 'Aanstelling commissieleden'), (2, 'Beoordeling door commissie'), (3, 'Afsluiting door secretaris'), (4, 'Afgesloten')])),
                ('short_route', models.BooleanField(default=True, verbose_name='Route')),
                ('go', models.NullBooleanField(default=None, verbose_name='Beslissing')),
                ('continuation', models.PositiveIntegerField(default=0, verbose_name='Afhandeling', choices=[(0, 'Goedkeuring door ETCL'), (1, 'Afwijzing door ETCL'), (2, 'Open review met lange (4-weken) route'), (3, 'Laat opnieuw beoordelen door METC')])),
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
