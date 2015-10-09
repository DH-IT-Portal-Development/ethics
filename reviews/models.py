from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from proposals.models import Proposal


class Review(models.Model):
    go = models.NullBooleanField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True)
    proposal = models.ForeignKey(Proposal)

    def __unicode__(self):
        return 'Review of %s' % self.proposal


class Decision(models.Model):
    go = models.BooleanField(default=False)
    review = models.ForeignKey(Review)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL)
    comments = models.TextField(
        _('Ruimte voor eventuele opmerkingen'),
        blank=True)

    def __unicode__(self):
        return 'Decision by %s on %s: %s' % (self.reviewer.username, self.review.proposal, self.go)
