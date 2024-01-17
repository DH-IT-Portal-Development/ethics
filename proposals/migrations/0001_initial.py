# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import main.validators
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Funding",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("order", models.PositiveIntegerField(unique=True)),
                ("description", models.CharField(max_length=200)),
                ("needs_details", models.BooleanField(default=False)),
                ("requires_review", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Proposal",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("reference_number", models.CharField(unique=True, max_length=16)),
                (
                    "date_start",
                    models.DateField(
                        null=True,
                        verbose_name="Wat is, indien bekend, de beoogde startdatum van uw studie?",
                        blank=True,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="De titel die u hier opgeeft is zichtbaar voor de ETCL-leden en, wanneer de studie is goedgekeurd, ook voor alle UiL-OTS medewerkers die in het archief van deze portal kijken. De titel mag niet identiek zijn aan een vorige titel van een studie die u heeft ingediend.",
                        unique=True,
                        max_length=200,
                        verbose_name="Wat is de titel van uw studie?",
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        verbose_name="Geef een duidelijke, bondige beschrijving van de onderzoeksvraag of -vragen. Gebruik maximaal 200 woorden.",
                        validators=[main.validators.MaxWordsValidator(200)],
                    ),
                ),
                (
                    "other_applicants",
                    models.BooleanField(
                        default=False,
                        verbose_name="Zijn er nog andere UiL OTS-onderzoekers of -studenten bij deze studie betrokken?",
                    ),
                ),
                (
                    "other_stakeholders",
                    models.BooleanField(
                        default=False,
                        verbose_name="Zijn er onderzoekers van buiten UiL OTS bij deze studie betrokken?",
                    ),
                ),
                (
                    "stakeholders",
                    models.TextField(verbose_name="Andere betrokkenen", blank=True),
                ),
                (
                    "funding_details",
                    models.CharField(
                        max_length=200, verbose_name="Namelijk", blank=True
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        verbose_name="Ruimte voor eventuele opmerkingen", blank=True
                    ),
                ),
                ("pdf", models.FileField(upload_to=b"", blank=True)),
                (
                    "studies_similar",
                    models.NullBooleanField(
                        help_text="Daar waar de verschillen klein en qua belasting of risico irrelevant zijn is sprake van in essentie hetzelfde traject. Denk hierbij aan taakonderzoek waarin de ene groep in taak X de ene helft van een set verhaaltjes te lezen krijgt, en de andere groep in taak X de andere helft. Of aan interventieonderzoek waarin drie vergelijkbare groepen op hetzelfde moment een verschillende interventie-variant krijgen (specificeer dan wel bij de beschrijving van de interventie welke varianten precies gebruikt worden).",
                        verbose_name="Doorlopen alle deelnemersgroepen in essentie hetzelfde traject?",
                    ),
                ),
                (
                    "studies_number",
                    models.PositiveIntegerField(
                        default=1,
                        verbose_name="Hoeveel verschillende trajecten zijn er?",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                (
                    "status",
                    models.PositiveIntegerField(
                        default=1,
                        choices=[
                            (1, "Concept"),
                            (
                                40,
                                "Opgestuurd ter beoordeling door eindverantwoordelijke",
                            ),
                            (50, "Opgestuurd ter beoordeling door ETCL"),
                            (55, "Studie is beoordeeld door ETCL"),
                            (60, "Studie is beoordeeld door METC"),
                        ],
                    ),
                ),
                ("status_review", models.NullBooleanField(default=None)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("date_submitted_supervisor", models.DateTimeField(null=True)),
                ("date_reviewed_supervisor", models.DateTimeField(null=True)),
                ("date_submitted", models.DateTimeField(null=True)),
                ("date_reviewed", models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Relation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("order", models.PositiveIntegerField(unique=True)),
                ("description", models.CharField(max_length=200)),
                ("needs_supervisor", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Wmo",
            fields=[
                (
                    "metc",
                    models.CharField(
                        default=None,
                        max_length=1,
                        verbose_name="Vindt de dataverzameling plaats binnen het UMC Utrecht of andere instelling waar toetsing door een METC verplicht is gesteld?",
                        choices=[(b"Y", "ja"), (b"N", "nee"), (b"?", "twijfel")],
                    ),
                ),
                (
                    "metc_details",
                    models.TextField(verbose_name="Licht toe", blank=True),
                ),
                (
                    "metc_institution",
                    models.CharField(
                        max_length=200, verbose_name="Welke instelling?", blank=True
                    ),
                ),
                (
                    "is_medical",
                    models.CharField(
                        blank=True,
                        help_text="De definitie van medisch-wetenschappelijk onderzoek is: Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het beantwoorden van een vraag op het gebied van ziekte en gezondheid (etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, uitkomst of behandeling van ziekte), door het op systematische wijze vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen aan medische kennis die ook geldend is voor populaties buiten de directe onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk onderzoek, 2005, ccmo.nl)",
                        max_length=1,
                        verbose_name="Is de onderzoeksvraag medisch-wetenschappelijk van aard (zoals gedefinieerd door de WMO)?",
                        choices=[(b"Y", "ja"), (b"N", "nee"), (b"?", "twijfel")],
                    ),
                ),
                (
                    "is_behavioristic",
                    models.CharField(
                        blank=True,
                        help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een deelnemer tot de deelnemer een knop/toets in laten drukken. Bij observatieonderzoek waarbij er niets van de deelnemers gevraagd wordt, deze dus uitsluitend geobserveerd worden in hun leven zoals het ook had plaatsgevonden zonder de observatie, slechts dan kan "nee" ingevuld worden.',
                        max_length=1,
                        verbose_name="Worden de deelnemers aan een handeling onderworpen of worden hen gedragsregels opgelegd (zoals gedefinieerd door de WMO)?",
                        choices=[(b"Y", "ja"), (b"N", "nee"), (b"?", "twijfel")],
                    ),
                ),
                (
                    "metc_application",
                    models.BooleanField(
                        default=False,
                        verbose_name="Uw studie moet beoordeeld worden door de METC, maar dient nog wel bij de ETCL te worden geregistreerd. Is deze studie al aangemeld bij een METC?",
                    ),
                ),
                (
                    "metc_decision",
                    models.BooleanField(
                        default=False,
                        verbose_name="Is de METC al tot een beslissing gekomen?",
                    ),
                ),
                (
                    "metc_decision_pdf",
                    models.FileField(
                        blank=True,
                        upload_to=b"",
                        verbose_name="Upload hier de beslissing van het METC (in .pdf of .doc(x)-formaat)",
                        validators=[main.validators.validate_pdf_or_doc],
                    ),
                ),
                (
                    "status",
                    models.PositiveIntegerField(
                        default=0,
                        choices=[
                            (0, "Geen beoordeling door METC noodzakelijk"),
                            (1, "In afwachting beslissing METC"),
                            (2, "Beslissing METC ge\xfcpload"),
                        ],
                    ),
                ),
                ("enforced_by_commission", models.BooleanField(default=False)),
                (
                    "proposal",
                    models.OneToOneField(
                        primary_key=True,
                        serialize=False,
                        to="proposals.Proposal",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="proposal",
            name="applicants",
            field=models.ManyToManyField(
                help_text="Als uw medeonderzoeker niet in de lijst voorkomt, vraag hem dan een keer in te loggen in het webportaal.",
                related_name="applicants",
                verbose_name="Uitvoerende(n) (inclusief uzelf)",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="created_by",
            field=models.ForeignKey(
                related_name="created_by",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="funding",
            field=models.ManyToManyField(
                to="proposals.Funding",
                verbose_name="Hoe wordt dit onderzoek gefinancierd?",
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="parent",
            field=models.ForeignKey(
                verbose_name="Te kopi\xebren studie",
                on_delete=models.CASCADE,
                to="proposals.Proposal",
                help_text="Dit veld toont enkel studies waar u zelf een medeuitvoerende bent.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="relation",
            field=models.ForeignKey(
                verbose_name="In welke hoedanigheid bent u betrokken bij deze UiL OTS studie?",
                to="proposals.Relation",
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="proposal",
            name="supervisor",
            field=models.ForeignKey(
                blank=True,
                to=settings.AUTH_USER_MODEL,
                help_text="Aan het einde van de procedure kunt u deze studie ter verificatie naar uw eindverantwoordelijke sturen. De eindverantwoordelijke zal de studie vervolgens kunnen aanpassen en indienen bij de ETCL.",
                null=True,
                verbose_name="Eindverantwoordelijke onderzoeker",
                on_delete=models.CASCADE,
            ),
        ),
    ]
