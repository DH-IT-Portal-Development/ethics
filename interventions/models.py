from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import SettingModel
from studies.models import Study


class Intervention(SettingModel):
    period = models.TextField(
        _('Wat is de periode waarbinnen de interventie plaatsvindt?'))
    amount_per_week = models.PositiveIntegerField(
        _('Hoe vaak per week vindt de interventiesessie plaats?'))
    duration = models.PositiveIntegerField(
        _('Wat is de duur van de interventie per sessie in minuten?'))
    measurement = models.TextField(
        _('Hoe wordt het effect van de interventie gemeten?'),
        help_text=_('Wanneer u de deelnemer extra taken laat uitvoeren, \
dus een taak die niet behoort tot het reguliere onderwijspakket, dan moet \
u op de vorige pagina ook "takenonderzoek" aanvinken.'))

    experimenter = models.TextField(
        _('Wie voert de interventie uit?'))
    description = models.TextField(
        _('Geef een beschrijving van de experimentele interventie'))
    has_controls = models.BooleanField(
        _('Is er sprake van een controlegroep?'),
        default=False)
    controls_description = models.TextField(
        _('Geef een beschrijving van de controleinterventie'),
        blank=True)

    # References
    study = models.OneToOneField(Study)
