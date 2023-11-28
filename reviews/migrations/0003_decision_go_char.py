# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from reviews.models import Decision


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return

    for decision in apps.get_model('reviews', 'decision').objects.all():
        if decision.go is None:
            decision.go_char = ''
        elif decision.go:
            decision.go_char = Decision.Approval.APPROVED
        else:
            decision.go_char = Decision.Approval.NOT_APPROVED

        decision.save()


def backwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return

    for decision in apps.get_model('reviews', 'decision').objects.all():
        if decision.go_char == Decision.Approval.APPROVED:
            decision.go = True
        elif decision.go_char == Decision.Approval.NOT_APPROVED:
            decision.go = False
        else:
            decision.go = None

        decision.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20160927_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='go_char',
            field=models.CharField(blank=True, max_length=1, verbose_name='Beslissing', choices=[(b'Y', 'goedgekeurd'), (b'N', 'niet goegekeurd'), (b'?', 'revisie noodzakelijk')]),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name='decision',
            name='go',
        ),
        migrations.RenameField(
            model_name='decision',
            old_name='go_char',
            new_name='go',
        ),
    ]
