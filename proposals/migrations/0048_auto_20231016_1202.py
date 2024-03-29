# Generated by Django 3.2.20 on 2023-10-16 10:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("proposals", "0047_auto_20230718_1626"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="applicants",
            field=models.ManyToManyField(
                related_name="applicants",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Uitvoerenden, inclusief uzelf. Let op! De andere onderzoekers moeten         ten minste één keer zijn ingelogd op dit portaal om ze te kunnen selecteren.",
            ),
        ),
        migrations.AlterField(
            model_name="proposal",
            name="embargo",
            field=models.BooleanField(
                blank=True,
                default=None,
                null=True,
                verbose_name="Als de deelnemers van je onderzoek moeten worden misleid, kan           je ervoor kiezen je applicatie pas later op te laten nemen in het           publieke archief en het archief voor gebruikers           van dit portaal. Wil je dat jouw onderzoek tijdelijk onder           embargo wordt geplaatst?",
            ),
        ),
    ]
