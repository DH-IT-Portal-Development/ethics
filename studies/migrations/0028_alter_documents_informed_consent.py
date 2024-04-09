# Generated by Django 3.2.20 on 2024-04-09 12:48

from django.db import migrations, models
import main.validators
import proposals.utils.proposal_utils


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0027_auto_20230227_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='informed_consent',
            field=models.FileField(blank=True, help_text='Bij algemeen belang, dien hier s.v.p. een leeg Word document in.', storage=proposals.utils.proposal_utils.OverwriteStorage(), upload_to=proposals.utils.proposal_utils.FilenameFactory('Informed_Consent'), validators=[main.validators.validate_pdf_or_doc], verbose_name='Upload hier de toestemmingsverklaring (in .pdf of .doc(x)-formaat)'),
        ),
    ]
