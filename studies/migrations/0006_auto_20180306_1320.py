# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import main.validators


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0005_auto_20180302_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='director_consent_declaration',
            field=models.FileField(validators=[main.validators.validate_pdf_or_doc], upload_to=b'', blank=True, help_text=b'If it is already signed, upload the signed declaration form. If it is not signed yet, you can upload the unsigned document and send the document when it is signed to the secretary of the EtCL', verbose_name='Upload hier de toestemmingsverklaring van de schoolleider/hoofd van het departement (in .pdf of .doc(x)-format)'),
        ),
        migrations.AlterField(
            model_name='study',
            name='director_consent_information',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief voor de schoolleider/hoofd van het departement (in .pdf of .doc(x)-formaat)', validators=[main.validators.validate_pdf_or_doc]),
        ),
        migrations.AlterField(
            model_name='study',
            name='parents_information',
            field=models.FileField(blank=True, upload_to=b'', verbose_name='Upload hier de informatiebrief voor de ouders (in .pdf of .doc(x)-formaat)', validators=[main.validators.validate_pdf_or_doc]),
        ),
        migrations.AlterField(
            model_name='study',
            name='passive_consent',
            field=models.NullBooleanField(help_text='Wanneer u kinderen via een instelling (dus ook school) werft en u de ouders niet laat ondertekenen, maar in plaats daarvan de leiding van die instelling, dan maakt u gebruik van passieve informed consent. U kunt de templates vinden op <a href="https://etcl.wp.hum.uu.nl/toestemmingsverklaringen/" target="_blank">de ETCL-website</a>.', verbose_name='Maakt u gebruik van passieve informed consent?'),
        ),
    ]
