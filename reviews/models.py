from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from proposals.models import Proposal


class Review(models.Model):
    SUPERVISOR = 0
    ASSIGNMENT = 1
    COMMISSION = 2
    STAGES = (
        (SUPERVISOR, _('Beoordeling door eindverantwoordelijke')),
        (ASSIGNMENT, _('Aanstelling commissieleden')),
        (COMMISSION, _('Beoordeling door ethische commissie')),
    )

    GO = 0
    NO_GO = 1
    LONG_ROUTE = 2
    METC = 3
    CONTINUATIONS = (
        (GO, _('Goedkeuring door ETCL')),
        (NO_GO, _('Afwijzing door ETCL')),
        (LONG_ROUTE, _('Open review met lange (4-weken) route')),
        (METC, _('Laat opnieuw beoordelen door METC')),
    )

    stage = models.PositiveIntegerField(choices=STAGES, default=SUPERVISOR)
    short_route = models.BooleanField(_('Route'), default=True)
    go = models.NullBooleanField(_('Beslissing'), default=None)
    continuation = models.PositiveIntegerField(_('Afhandeling'), choices=CONTINUATIONS, default=GO)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    proposal = models.ForeignKey(Proposal)

    def update_go(self):
        """
        Check all decisions: if all are finished, set the final decision and date_end.
        """
        all_decisions = self.decision_set.count()
        closed_decisions = 0
        final_go = True
        for decision in self.decision_set.all():
            if decision.go is not None:
                closed_decisions += 1
                final_go &= decision.go

        if all_decisions == closed_decisions:
            self.go = final_go
            self.save()

            # For a supervisor review:
            if self.stage == self.SUPERVISOR:
                # Update the status of the Proposal with the end dates
                self.proposal.date_reviewed_supervisor = self.date_end
                self.proposal.save()
                # Set the Review end date to now
                self.date_end = timezone.now()
                self.save()
                # On GO, start the assignment phase
                if self.go:
                    from .utils import start_assignment_phase
                    start_assignment_phase(self.proposal)

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
        """
        Sets the correct status of the Review on save of a Decision.
        """
        super(Decision, self).save(*args, **kwargs)
        self.review.update_go()

    def __unicode__(self):
        return 'Decision by %s on %s: %s' % (self.reviewer.username, self.review.proposal, self.go)
