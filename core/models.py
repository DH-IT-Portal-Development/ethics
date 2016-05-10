from django.db import models
from django.utils.translation import ugettext as _

YES = 'Y'
NO = 'N'
DOUBT = '?'
YES_NO_DOUBT = (
    (YES, _('ja')),
    (NO, _('nee')),
    (DOUBT, _('twijfel')),
)


class Setting(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    needs_supervision = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description
