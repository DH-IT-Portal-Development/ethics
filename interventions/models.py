from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import Setting
from studies.models import Study


class Intervention(models.Model):
    setting = models.ManyToManyField(
        Setting,
        verbose_name=_('Geef aan waar de dataverzameling plaatsvindt'))
    setting_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    supervision = models.NullBooleanField(
        _('Vindt het afnemen van de taak plaats onder het toeziend oog \
van de leraar of een ander persoon die bevoegd is?')
    )

    number = models.PositiveIntegerField(
        _('Uit hoeveel sessies bestaat de interventie?'))
    duration = models.PositiveIntegerField(
        _('Wat is de duur van de sessie(s)?'))
    experimenter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Wie voert de voor- en nameting uit?'),
        related_name='experimenter')
    description = models.TextField(
        _('Geef een beschrijving van de experimentele interventie'))

    has_controls = models.BooleanField(
        _('Is er sprake van een controlegroep?'),
        default=False)
    has_controls_details = models.TextField(
        _('Geef een beschrijving van de controleinterventie'),
        blank=True)

    has_recording = models.BooleanField(
        _('Is er sprake van een voor- en een nameting?'),
        default=False)
    recording_same_experimenter = models.BooleanField(
        _('Is de afnemer van de voor- en nameting dezelfde persoon als die de interventie afneemt?'),
        default=True)
    recording_experimenter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Wie voert de voor- en nameting uit?'),
        related_name='recording_experimenter',
        blank=True,
        null=True)

    # References
    study = models.OneToOneField(Study)
