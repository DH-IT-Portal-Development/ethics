# Generated by Django 2.2.24 on 2021-09-20 14:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0010_auto_20210809_1653"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="continuation",
            field=models.PositiveIntegerField(
                choices=[
                    (0, "Goedkeuring door FETC-GW"),
                    (1, "Revisie noodzakelijk"),
                    (2, "Afwijzing door FETC-GW"),
                    (3, "Open review met lange (4-weken) route"),
                    (4, "Laat opnieuw beoordelen door METC"),
                    (5, "Positief advies van FETC-GW, post-hoc"),
                    (6, "Negatief advies van FETC-GW, post-hoc"),
                    (7, "Niet verder in behandeling genomen"),
                ],
                default=0,
                verbose_name="Afhandeling",
            ),
        ),
    ]
