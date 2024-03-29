# Generated by Django 2.2.17 on 2021-01-25 10:59

from django.db import migrations, models
import django.db.models.deletion
import main.validators
import proposals.utils.proposal_utils


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0027_auto_20210118_1735"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="parent",
            field=models.ForeignKey(
                help_text="Dit veld toont enkel studies waar u zelf een medeuitvoerende bent.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="proposals.Proposal",
                verbose_name="Te kopiëren studie",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="pdf",
            field=models.FileField(
                blank=True,
                storage=proposals.utils.proposal_utils.OverwriteStorage(),
                upload_to=proposals.utils.proposal_utils.FilenameFactory("Proposal"),
            ),
        ),
        migrations.AlterField(
            model_name="wmo",
            name="metc_decision_pdf",
            field=models.FileField(
                blank=True,
                storage=proposals.utils.proposal_utils.OverwriteStorage(),
                upload_to=proposals.utils.proposal_utils.FilenameFactory(
                    "METC_Decision"
                ),
                validators=[main.validators.validate_pdf_or_doc],
                verbose_name="Upload hier de beslissing van het METC (in .pdf of .doc(x)-formaat)",
            ),
        ),
    ]
