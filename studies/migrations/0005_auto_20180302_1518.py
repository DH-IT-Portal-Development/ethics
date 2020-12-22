# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import main.validators


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0004_auto_20170601_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='director_consent_declaration',
            field=models.FileField(validators=[main.validators.validate_pdf_or_doc], upload_to=b'', blank=True, help_text=b'If it is already signed, upload the signed declaration form. If it is not signed yet, you can upload the unsigned document and send the document when it is signed to the secretary of the EtCL', verbose_name=b'Please upload the declaration of consent for the school director/head of the department (in .pdf of .doc(x)-formaat)'),
        ),
        migrations.AddField(
            model_name='study',
            name='director_consent_information',
            field=models.FileField(blank=True, upload_to=b'', verbose_name=b'Please upload the the information letter for the school director/head of the department (in .pdf of .doc(x)-formaat)', validators=[main.validators.validate_pdf_or_doc]),
        ),
        migrations.AddField(
            model_name='study',
            name='parents_information',
            field=models.FileField(blank=True, upload_to=b'', verbose_name=b'Please upload the information letter for the parents here (in .pdf of .doc(x)-formaat)', validators=[main.validators.validate_pdf_or_doc]),
        ),
    ]
