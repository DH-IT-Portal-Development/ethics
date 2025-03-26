# Generated by Django 4.2.17 on 2025-03-26 12:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0033_alter_documents_informed_consent"),
    ]

    operations = [
        migrations.CreateModel(
            name="Registration",
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
                ("order", models.PositiveIntegerField(unique=True)),
                ("description", models.CharField(max_length=200)),
                ("description_nl", models.CharField(max_length=200, null=True)),
                ("description_en", models.CharField(max_length=200, null=True)),
                ("is_local", models.BooleanField(default=False)),
                ("needs_details", models.BooleanField(default=False)),
                ("needs_kind", models.BooleanField(default=False)),
                ("requires_review", models.BooleanField(default=False)),
                ("age_min", models.PositiveIntegerField(blank=True, null=True)),
                ("is_recording", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Vastlegging gedrag",
                "ordering": ["order"],
            },
        ),
        migrations.AddField(
            model_name="study",
            name="registration_kinds_details",
            field=models.TextField(blank=True, max_length=1500, verbose_name="Namelijk"),
        ),
        migrations.AddField(
            model_name="study",
            name="registrations_details",
            field=models.TextField(blank=True, max_length=1500, verbose_name="Namelijk"),
        ),
        migrations.CreateModel(
            name="RegistrationKind",
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
                ("order", models.PositiveIntegerField(unique=True)),
                ("description", models.CharField(max_length=200)),
                ("description_nl", models.CharField(max_length=200, null=True)),
                ("description_en", models.CharField(max_length=200, null=True)),
                ("needs_details", models.BooleanField(default=False)),
                ("requires_review", models.BooleanField(default=False)),
                (
                    "registration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studies.registration",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.AddField(
            model_name="study",
            name="registration_kinds",
            field=models.ManyToManyField(
                blank=True,
                to="studies.registrationkind",
                verbose_name="Kies het soort meting",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="registrations",
            field=models.ManyToManyField(
                help_text="Opnames zijn nooit anoniem en niet te anonimiseren. Let hierop bij het gebruik van de term 'anoniem' of 'geanonimiseerd' in je documenten voor deelnemers. Voor meer informatie, zie het UU Data Privacy Handbook over <a href='https://utrechtuniversity.github.io/dataprivacyhandbook/pseudonymisation-anonymisation.html#pseudonymisation-anonymisation' target='_blank'>anonimiseren en pseudonimiseren</a>.",
                to="studies.registration",
                verbose_name="Hoe wordt het gedrag of de toestand van de deelnemer bij deze studie vastgelegd?",
            ),
        ),
    ]
