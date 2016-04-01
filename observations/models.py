from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from studies.models import Study


class Observation(models.Model):
    days = models.PositiveIntegerField(
        _('Op hoeveel dagen wordt er geobserveerd?'))
    mean_hours = models.DecimalField(
        _('Hoeveel uur wordt er gemiddeld per dag geobserveerd?'),
        max_digits=4,
        decimal_places=2,
        validators=[MaxValueValidator(24)])
    is_anonymous = models.BooleanField(
        _('Weten de deelnemers dat ze deelnemer zijn, ofwel, wordt er anoniem geobserveerd?'),
        help_text=_('Zoals zou kunnen voorkomen op fora en de onderzoeker ook een account heeft.'),
        default=False)
    is_test = models.BooleanField(
        _('Doet de onderzoeker zich voor als behorende tot de doelgroep?'),
        default=False)

    # References
    study = models.OneToOneField(Study)


class Location(models.Model):
    name = models.CharField(_('Locatie'), max_length=200)
    registration = models.TextField(_('Hoe wordt het gedrag geregistreerd?'))
    observation = models.ForeignKey(Observation)

    def __unicode__(self):
        return self.name
