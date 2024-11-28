from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from main.models import SettingModel
from main.validators import validate_pdf_or_doc
from studies.models import Study


class Registration(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Observation(SettingModel):
    # This is used internally to provide backwards compatibility with the old
    # version of this model. All old fields are still used if this is 1.
    version = models.PositiveIntegerField(
        "INTERNAL - Describes which version of the observation model is used", default=2
    )

    details_who = models.TextField(
        _("Beschrijf <b>wie</b> er wordt geobserveerd."),
        help_text=_(
            "Maak duidelijk voor de commissie wie er wordt geobserveerd en wat er precies van de deelnemer wordt"
            " geobserveerd. Bijvoorbeeld: De leraar zal geobserveerd worden. De observatie moet de interactie "
            "tussen leraar en leerling in kaart brengen."
        ),
        blank=True,
    )

    details_why = models.TextField(
        _("Beschrijf <b>waarom</b> er wordt geobserveerd."),
        help_text=_(
            "Wat is het doel van de observatie? Bijvoorbeeld: Het doel van de "
            "observatie is inzicht te krijgen in hoe de leerkracht omgaat met "
            "de uitleg van de nieuwe lesmethode. Doet die dat op de gewenste "
            "manier en in begrijpelijke taal?"
        ),
        blank=True,
    )

    details_frequency = models.TextField(
        _("Beschrijf <b>hoe vaak en hoe lang</b> de observant wordt geobserveerd."),
        help_text=_(
            "Bijvoorbeeld: De leraar zal 5 lessen van 45 minuten "
            "worden geobserveerd."
        ),
        blank=True,
    )

    is_anonymous = models.BooleanField(
        _("Wordt er anoniem geobserveerd?"),
        help_text=_(
            "Zoals zou kunnen voorkomen op fora en de onderzoeker ook een account heeft."
        ),
        default=False,
    )

    is_anonymous_details = models.TextField(
        _("Licht toe"),
        blank=True,
    )

    is_in_target_group = models.BooleanField(
        _("Doet de onderzoeker zich voor als behorende tot de doelgroep?"),
        default=False,
    )

    is_in_target_group_details = models.TextField(
        _("Licht toe"),
        blank=True,
    )

    is_nonpublic_space = models.BooleanField(
        _("Wordt er geobserveerd in een niet-openbare ruimte?"),
        help_text=_(
            "Bijvoorbeeld er wordt geobserveerd bij iemand thuis, tijdens een "
            "hypotheekgesprek, tijdens politieverhoren of een digitale "
            "omgeving waar een account voor moet worden aangemaakt."
        ),
        default=False,
    )

    is_nonpublic_space_details = models.TextField(
        _("Licht toe"),
        blank=True,
    )

    has_advanced_consent = models.BooleanField(
        _("Wordt er van tevoren toestemming gegeven?"),
        default=True,
    )

    has_advanced_consent_details = models.TextField(
        _(
            "Leg uit waarom er niet van tevoren toestemming wordt gegeven en "
            "beschrijf ook op welke wijze dit achteraf verzorgd wordt."
        ),
        blank=True,
    )

    needs_approval = models.BooleanField(
        _(
            "Heb je toestemming nodig van een (samenwerkende) instantie \
om deze observatie te mogen uitvoeren?"
        ),
        default=False,
    )

    approval_institution = models.CharField(
        _("Welke instantie?"),
        max_length=200,
        blank=True,
    )

    approval_document = models.FileField(
        _("Upload hier het toestemmingsdocument (in .pdf of .doc(x)-formaat)"),
        blank=True,
        validators=[validate_pdf_or_doc],
    )

    registrations = models.ManyToManyField(
        Registration,
        help_text=_(
            "Opnames zijn nooit anoniem en niet te anonimiseren. Let hierop bij het gebruik van de term ‘anoniem’ of ‘geanonimiseerd’ in je documenten voor deelnemers. Voor meer informatie, zie de <a href='https://fetc-gw.wp.hum.uu.nl/wp-content/uploads/sites/336/2021/12/FETC-GW-Richtlijnen-voor-geinformeerde-toestemming-bij-wetenschappelijk-onderzoek-versie-1.1_21dec2021.pdf' target='_blank'>Richtlijnen voor geïnformeerde toestemming, ‘Beeld en geluid’</a>."
        ),
        verbose_name=_("Hoe wordt het gedrag geregistreerd?"),
    )

    registrations_details = models.CharField(_("Namelijk"), max_length=200, blank=True)

    # Legacy, only used in v1
    days = models.PositiveIntegerField(
        _("Op hoeveel dagen wordt er geobserveerd (per deelnemer)?"),
        blank=True,
        null=True,
    )
    mean_hours = models.DecimalField(
        _("Hoeveel uur wordt er gemiddeld per dag geobserveerd?"),
        max_digits=4,
        decimal_places=2,
        validators=[MaxValueValidator(24)],
        blank=True,
        null=True,
    )

    # References
    study = models.OneToOneField(Study, on_delete=models.CASCADE)
