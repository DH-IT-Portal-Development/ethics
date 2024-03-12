# Generated by Django 2.2.20 on 2021-05-28 11:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0005_auto_20180829_1540"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemMessage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.CharField(max_length=200)),
                (
                    "level",
                    models.IntegerField(
                        choices=[(1, "Urgent"), (2, "Attention"), (3, "Info")]
                    ),
                ),
                ("not_before", models.DateTimeField()),
                ("not_after", models.DateTimeField()),
            ],
        ),
    ]
