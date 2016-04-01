from django.db import models
from django.utils.translation import ugettext_lazy as _

from studies.models import Study


class Intervention(models.Model):
    description = models.TextField(_('Beschrijf de interventie. Geef daarbij aan in welke precieze setting(s) \
in hoe veel sessies welke precieze veranderingen worden doorgevoerd, en welke partijen er bij betrokken zijn.'))
    has_drawbacks = models.BooleanField(
        _('Is de interventie zodanig dat er voor de deelnemers ook nadelen aan verbonden kunnen zijn?'),
        help_text=_('Denk aan een verminderde leeropbrengst, een minder effectief 112-gesprek, \
een slechter adviesgesprek, een ongunstiger beoordeling, etc'),
        default=False)
    has_drawbacks_details = models.CharField(
        _('Licht toe'),
        max_length=200,
        blank=True)

    # References
    study = models.OneToOneField(Study)
