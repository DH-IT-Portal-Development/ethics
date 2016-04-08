# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0004_auto_20160408_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='registrations_details',
            field=models.CharField(max_length=200, verbose_name='Namelijk', blank=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='approval_document',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hiet het toestemmingsdocument (in .pdf of .doc(x)-formaat)', validators=[core.validators.validate_pdf_or_doc]),
        ),
        migrations.AddField(
            model_name='observation',
            name='approval_institution',
            field=models.CharField(max_length=200, verbose_name='Welke instantie?', blank=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='needs_approval',
            field=models.BooleanField(default=False, verbose_name='Heeft u toestemming nodig van een (samenwerkende) instantie om deze observatie te mogen uitvoeren?'),
        ),
    ]
