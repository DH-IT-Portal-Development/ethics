# Generated by Django 2.2.17 on 2021-01-12 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0025_merge_20201222_1654"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="applicants",
            field=models.ManyToManyField(
                related_name="applicants",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Uitvoerende(n) (inclusief uzelf)",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="parent",
            field=models.ForeignKey(
                help_text="Dit veld toont enkel studies waar u zelf een medeuitvoerende bent.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="proposals.Proposal",
                verbose_name="Te kopiëren studie",
            ),
        ),
    ]
