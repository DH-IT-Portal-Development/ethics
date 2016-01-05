# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import proposals.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_auto_20160105_1004'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='briefing_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief (in PDF-formaat)', validators=[proposals.models.validate_pdf]),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='informed_consent_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de toestemmingsverklaring (in PDF-formaat)', validators=[proposals.models.validate_pdf]),
        ),
    ]
