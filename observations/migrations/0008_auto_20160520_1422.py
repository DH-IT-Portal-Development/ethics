# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0007_auto_20160503_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='approval_document',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier het toestemmingsdocument (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc]),
        ),
        migrations.AlterField(
            model_name='observation',
            name='has_advanced_consent',
            field=models.BooleanField(default=True, verbose_name='Vindt informed consent van tevoren plaats?'),
        ),
    ]
