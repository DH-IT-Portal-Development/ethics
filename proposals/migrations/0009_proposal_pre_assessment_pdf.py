# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_relation_check_pre_assessment'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='pre_assessment_pdf',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier uw aanvraag (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc]),
        ),
    ]
