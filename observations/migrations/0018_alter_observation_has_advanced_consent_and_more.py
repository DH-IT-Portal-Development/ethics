# Generated by Django 4.2.11 on 2024-12-05 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0017_registration_is_recording"),
    ]

    operations = [
        migrations.AlterField(
            model_name="observation",
            name="has_advanced_consent",
            field=models.BooleanField(
                default=True, verbose_name="Wordt er van tevoren toestemming gegeven?"
            ),
        ),
        migrations.AlterField(
            model_name="observation",
            name="has_advanced_consent_details",
            field=models.TextField(
                blank=True,
                verbose_name="Leg uit waarom er niet van tevoren toestemming wordt gegeven en beschrijf ook op welke wijze dit achteraf verzorgd wordt.",
            ),
        ),
        migrations.AlterField(
            model_name="observation",
            name="is_nonpublic_space",
            field=models.BooleanField(
                default=False,
                help_text="Bijvoorbeeld: er wordt geobserveerd bij iemand thuis, tijdens een hypotheekgesprek, tijdens politieverhoren of een digitale omgeving waar een account voor moet worden aangemaakt.",
                verbose_name="Wordt er geobserveerd in een niet-openbare ruimte?",
            ),
        ),
        migrations.AlterField(
            model_name="observation",
            name="registrations",
            field=models.ManyToManyField(
                help_text="Opnames zijn nooit anoniem en niet te anonimiseren. Let hierop bij het gebruik van de term 'anoniem' of 'geanonimiseerd' in je documenten voor deelnemers. Voor meer informatie, zie het UU Data Privacy Handbook over <a href='https://utrechtuniversity.github.io/dataprivacyhandbook/pseudonymisation-anonymisation.html#pseudonymisation-anonymisation' target='_blank'>anonimiseren en pseudonimiseren</a>.",
                to="observations.registration",
                verbose_name="Hoe wordt het gedrag geregistreerd?",
            ),
        ),
    ]
