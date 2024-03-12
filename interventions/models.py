from django.db import models
from django.utils.translation import ugettext_lazy as _

from main.models import SettingModel
from studies.models import Study


class Intervention(SettingModel):
    # This is used internally to provide backwards compatibility with the old version of this model. All old fields are
    # still used if this is 1.
    version = models.PositiveIntegerField(
        "INTERNAL - Describes which version of the intervention model is used",
        default=2,
    )

    period = models.TextField(
        _("Wat is de periode waarbinnen de interventie plaatsvindt?"),
        help_text=_("De interventie vindt plaats binnen het schooljaar " "2018-2019"),
        blank=True,
    )

    multiple_sessions = models.BooleanField(
        _("Zal de interventie vaker dan één keer plaatsvinden?"),
        default=False,
    )

    session_frequency = models.TextField(
        _("Wat is de frequentie van de interventie?"),
        blank=True,
    )

    duration = models.PositiveIntegerField(
        _("Wat is de duur van de interventie per sessie in minuten?"),
        blank=True,
        null=True,
    )

    experimenter = models.TextField(
        _("Wie voert de interventie uit?"),
        blank=True,
    )

    description = models.TextField(
        _("Geef een beschrijving van de experimentele interventie"),
        blank=True,
    )

    has_controls = models.BooleanField(
        _(
            "Is er sprake van een controlegroep? (Let op: als de controlegroep \
ook een ander soort taken krijgt, moet je hier een apart traject \
voor aanmaken)"
        ),
        default=False,
    )

    controls_description = models.TextField(
        _("Geef een beschrijving van de controleinterventie"),
        blank=True,
    )

    measurement = models.TextField(
        _("Hoe wordt het effect van de interventie gemeten?"),
        help_text=_(
            'Wanneer je de deelnemer extra taken laat uitvoeren, \
dus een taak die niet behoort tot het reguliere onderwijspakket, dan moet \
je op de vorige pagina ook "takenonderzoek" aanvinken.'
        ),
        blank=True,
    )

    extra_task = models.BooleanField(
        _("Voert de leerling nog een taak uit die niet onder het leerplan valt?"),
        help_text=_(
            "Moet het nog een taak doen, zoals het invullen van een (onderzoeks)vragenlijst, die niet binnen de interventie zelf valt?"
        ),
        default=False,
    )

    # Legacy, not used in version 2 of the form
    amount_per_week = models.PositiveIntegerField(
        _("Hoe vaak per week vindt de interventiesessie plaats?"),
        blank=True,
        default=1,
    )

    # References
    study = models.OneToOneField(
        Study,
        on_delete=models.CASCADE,
    )
