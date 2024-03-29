# Generated by Django 3.2.13 on 2022-09-04 12:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0040_auto_20220830_1634"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="funding_name",
            field=models.CharField(
                blank=True,
                help_text="De titel die je hier opgeeft zal in de formele toestemmingsbrief gebruikt worden.",
                max_length=200,
                verbose_name="Wat is de naam van het gefinancierde project en wat is het projectnummer?",
            ),
        ),
    ]
