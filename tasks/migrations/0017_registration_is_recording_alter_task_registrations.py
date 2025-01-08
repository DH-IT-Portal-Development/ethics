# Generated by Django 4.2.11 on 2024-12-05 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0016_auto_20240304_1151"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="is_recording",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="task",
            name="registrations",
            field=models.ManyToManyField(
                help_text="Opnames zijn nooit anoniem en niet te anonimiseren. Let hierop bij het gebruik van de term 'anoniem' of 'geanonimiseerd' in je documenten voor deelnemers. Voor meer informatie, zie het UU Data Privacy Handbook over <a href='https://utrechtuniversity.github.io/dataprivacyhandbook/pseudonymisation-anonymisation.html#pseudonymisation-anonymisation' target='_blank'>anonimiseren en pseudonimiseren</a>.",
                to="tasks.registration",
                verbose_name="Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?",
            ),
        ),
    ]
