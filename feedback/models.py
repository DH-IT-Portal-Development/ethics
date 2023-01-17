from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

STATUS_CODES = (
    (1, _('Open')),
    (2, _('Opgepakt')),
    (3, _('Afgehandeld')),
)

PRIORITY_CODES = (
    (1, _('Laag')),
    (2, _('Gemiddeld')),
    (3, _('Hoog')),
)


class Feedback(models.Model):
    url = models.URLField()
    comment = models.TextField(_('Feedback'))
    priority = models.IntegerField(default=1, choices=PRIORITY_CODES)
    status = models.IntegerField(default=1, choices=STATUS_CODES)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
