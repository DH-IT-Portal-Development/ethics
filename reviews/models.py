from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

from proposals.models import Proposal


class Review(models.Model):
    SUPERVISOR = 0
    COMMISSION = 1
    STAGES = (
        (SUPERVISOR, _('Beoordeling door supervisor')),
        (COMMISSION, _('Beoordeling door ethische commissie')),
    )
    stage = models.PositiveIntegerField(choices=STAGES, default=SUPERVISOR)
    go = models.NullBooleanField(_('Beslissing'), default=None)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    proposal = models.ForeignKey(Proposal)

    def update_go(self):
        """Check all decisions: if all are finished, set the final decision and date_end."""
        all_decisions = self.decision_set.count()
        closed_decisions = 0
        final_go = True
        for decision in self.decision_set.all():
            if decision.go != None:
                closed_decisions += 1
                final_go &= decision.go

        if all_decisions == closed_decisions:
            self.date_end = timezone.now()
            self.go = final_go
            self.save()

    def __unicode__(self):
        return 'Review of %s' % self.proposal


class Decision(models.Model):
    go = models.NullBooleanField(_('Beslissing'), default=None)
    date_decision = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(
        _('Ruimte voor eventuele opmerkingen'),
        blank=True)

    review = models.ForeignKey(Review)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = ('review', 'reviewer',)

    def save(self, *args, **kwargs):
        """Sets the correct status of the Review on save of a Decision"""
        super(Decision, self).save(*args, **kwargs)
        self.review.update_go()

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

    if proposal.relation.needs_supervisor:
        review.stage = Review.SUPERVISOR
        review.save()

        proposal.date_submitted_supervisor = timezone.now()
        proposal.save()

        decision = Decision.objects.create(review=review, reviewer=proposal.supervisor)
        decision.save()
    else:
        review.stage = Review.COMMISSION
        review.save()

        proposal.date_submitted = timezone.now()
        proposal.save()

        for user in get_user_model().objects.filter(is_staff=True):
            decision = Decision.objects.create(review=review, reviewer=user)
            decision.save()

    return review
