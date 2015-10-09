from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

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


def start_review(proposal):
    """
    If the proposal has a supervisor:
    - Set date_submitted_supervisor to current date/time
    - Start a Review for this Proposal
    - (TODO) Send an e-mail to the supervisor

    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.save()

    if proposal.supervisor:
        proposal.date_submitted_supervisor = timezone.now()
        proposal.save()

        decision = Decision.objects.create(review=review, reviewer=proposal.supervisor)
        decision.save()
    else:
        proposal.date_submitted = timezone.now()
        proposal.save()

        for user in get_user_model().objects.filter(is_staff=True):
            decision = Decision.objects.create(review=review, reviewer=user)
            decision.save()
