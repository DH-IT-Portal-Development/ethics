# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import proposals.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0012_auto_20160311_2236'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='briefing_pdf',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='informed_consent_pdf',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='passive_consent',
        ),
        migrations.AddField(
            model_name='study',
            name='briefing_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief (in PDF-formaat)', validators=[proposals.models.validate_pdf_or_doc]),
        ),
        migrations.AddField(
            model_name='study',
            name='informed_consent_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de toestemmingsverklaring (in PDF-formaat)', validators=[proposals.models.validate_pdf_or_doc]),
        ),
        migrations.AddField(
            model_name='study',
            name='passive_consent',
            field=models.BooleanField(default=False, help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <link website?>', verbose_name='Maakt uw studie gebruik van passieve informed consent?'),
        ),
    ]
