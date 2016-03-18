# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import proposals.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0018_auto_20160315_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='briefing_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief (in .pdf of .doc(x)-formaat)', validators=[proposals.models.validate_pdf_or_doc]),
        ),
        migrations.AlterField(
            model_name='study',
            name='informed_consent_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)', validators=[proposals.models.validate_pdf_or_doc]),
        ),
        migrations.AlterField(
            model_name='wmo',
            name='metc_decision_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de beslissing van het METC (in .pdf of .doc(x)-formaat)', validators=[proposals.models.validate_pdf_or_doc]),
        ),
    ]
