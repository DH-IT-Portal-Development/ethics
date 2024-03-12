# Generated by Django 2.2.17 on 2021-01-29 16:17

from django.db import migrations, models
import main.validators
import proposals.utils.proposal_utils


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0028_auto_20210125_1159"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="pre_assessment_pdf",
            field=models.FileField(
                blank=True,
                upload_to=proposals.utils.proposal_utils.FilenameFactory(
                    "Preassessment"
                ),
                validators=[main.validators.validate_pdf_or_doc],
                verbose_name="Upload hier uw aanvraag (in .pdf of .doc(x)-formaat)",
            ),
        ),
    ]
