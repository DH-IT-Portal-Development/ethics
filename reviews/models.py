from django.conf import settings
from django.db import models
from proposals.models import Proposal

class Review(models.Model):
    status = models.BooleanField(default=False)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    proposal = models.ForeignKey(Proposal)

    def __unicode__(self):
        return 'Review of %s' % self.review.proposal
        
class Decision(models.Model):
    go = models.BooleanField(default=False)
    review = models.ForeignKey(Review)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return 'Decision by %s on %s: %s' % (self.applicant.username, self.review.proposal, self.go)
