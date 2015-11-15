from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

from proposals.models import Proposal


class Review(models.Model):
    SUPERVISOR = 0
    ASSIGNMENT = 1
    COMMISSION = 2
    STAGES = (
        (SUPERVISOR, _('Beoordeling door supervisor')),
        (ASSIGNMENT, _('Aanstelling commissieleden')),
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
