# Generated by Django 3.2.13 on 2022-06-07 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0008_auto_20220103_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervention',
            name='has_controls',
            field=models.BooleanField(default=False, verbose_name='Is er sprake van een controlegroep? (Let op: als de controlegroep ook een ander soort taken krijgt, moet je hier een apart traject voor aanmaken)'),
        ),
    ]
