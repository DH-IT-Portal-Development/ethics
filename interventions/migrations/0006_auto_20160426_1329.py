# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('interventions', '0005_auto_20160419_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intervention',
            name='has_drawbacks',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='has_drawbacks_details',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='is_supervised',
        ),
        migrations.AddField(
            model_name='intervention',
            name='duration',
            field=models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van de sessie(s)?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='experimenter',
            field=models.ForeignKey(related_name='experimenter', default=1, verbose_name='Wie voert de voor- en nameting uit?', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='has_controls',
            field=models.BooleanField(default=False, verbose_name='Is er sprake van een controle groep?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='has_controls_details',
            field=models.TextField(verbose_name='Geef een beschrijving van de controle interventie', blank=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='has_recording',
            field=models.BooleanField(default=False, verbose_name='Is er sprake van een voor- en een nameting?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='number',
            field=models.PositiveIntegerField(default=1, verbose_name='Uit hoeveel sessies bestaat de interventie?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='recording_experimenter',
            field=models.ForeignKey(related_name='recording_experimenter', verbose_name='Wie voert de voor- en nameting uit?', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='recording_same_experimenter',
            field=models.BooleanField(default=True, verbose_name='Is de afnemer van de voor- en nameting dezelfde persoon als die de interventie afneemt?'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='description',
            field=models.TextField(verbose_name='Geef een beschrijving van de experimentele interventie'),
        ),
    ]
