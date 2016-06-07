# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0007_auto_20160503_1235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intervention',
            old_name='has_controls_details',
            new_name='controls_description',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='has_recording',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='number',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='recording_experimenter',
        ),
        migrations.RemoveField(
            model_name='intervention',
            name='recording_same_experimenter',
        ),
        migrations.AddField(
            model_name='intervention',
            name='amount_per_week',
            field=models.PositiveIntegerField(default=1, verbose_name='Hoe vaak per week vindt de interventiesessie plaats?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='measurement',
            field=models.TextField(default='', help_text='Wanneer u de deelnemer extra taken laat uitvoeren, dus een taak die niet behoort tot het reguliere onderwijspakket, dan moet u op de vorige pagina ook "takenonderzoek" aanvinken.', verbose_name='Hoe wordt het effect van de interventie gemeten?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intervention',
            name='period',
            field=models.TextField(default='', verbose_name='Wat is de periode waarbinnen de interventie plaatsvindt?'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='intervention',
            name='duration',
            field=models.PositiveIntegerField(verbose_name='Wat is de duur van de interventie per sessie in minuten?'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='experimenter',
            field=models.TextField(verbose_name='Wie voert de interventie uit?'),
        ),
    ]
