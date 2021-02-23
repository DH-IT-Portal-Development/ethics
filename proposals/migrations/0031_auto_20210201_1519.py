# Generated by Django 2.2.17 on 2021-02-01 14:19

from django.db import migrations, models
import main.validators
import proposals.utils.proposal_utils


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0030_auto_20210201_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='pre_approval_pdf',
            field=models.FileField(blank=True, upload_to=proposals.utils.proposal_utils.FilenameFactory('Pre_Approval'), validators=[main.validators.validate_pdf_or_doc], verbose_name='Upload hier uw formele toestemmingsbrief van dit instituut (in .pdf of .doc(x)-formaat)'),
        ),
    ]