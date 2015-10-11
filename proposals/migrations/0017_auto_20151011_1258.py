# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import proposals.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0016_auto_20151009_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='informed_consent_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informed consent', validators=[proposals.models.validate_pdf]),
        ),
        migrations.AlterField(
            model_name='survey',
            name='survey_file',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Bestand', validators=[proposals.models.validate_pdf]),
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.PositiveIntegerField(default=0, verbose_name='Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak (exclusief instructie maar inclusief oefensessie)? Indien de taakduur per proefpersoon varieert (self-paced taak of task-to-criterion), geef dan het redelijkerwijs te verwachten maximum op.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(45)]),
        ),
        migrations.AlterField(
            model_name='task',
            name='registration_kind',
            field=models.ForeignKey(verbose_name='Kies het soort meting:', blank=True, to='proposals.RegistrationKind', null=True),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_decision_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de beslissing van het METC', validators=[proposals.models.validate_pdf]),
        ),
    ]
