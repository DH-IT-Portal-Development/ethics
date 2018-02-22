from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from proposals.models import Proposal


class Review(models.Model):
    SUPERVISOR = 0
    ASSIGNMENT = 1
    COMMISSION = 2
    CLOSING = 3
    CLOSED = 4
    STAGES = (
        (SUPERVISOR, _('Beoordeling door eindverantwoordelijke')),
        (ASSIGNMENT, _('Aanstelling commissieleden')),
        (COMMISSION, _('Beoordeling door commissie')),
        (CLOSING, _('Afsluiting door secretaris')),
        (CLOSED, _('Afgesloten')),
    )

    GO = 0
    REVISION = 1
    NO_GO = 2
    LONG_ROUTE = 3
    METC = 4
    CONTINUATIONS = (
        (GO, _('Goedkeuring door ETCL')),
        (REVISION, _('Revisie noodzakelijk')),
        (NO_GO, _('Afwijzing door ETCL')),
        (LONG_ROUTE, _('Open review met lange (4-weken) route')),
        (METC, _('Laat opnieuw beoordelen door METC')),
    )

    stage = models.PositiveIntegerField(choices=STAGES, default=SUPERVISOR)
    short_route = models.NullBooleanField(_('Route'), default=None)
    go = models.NullBooleanField(_('Beslissing'), default=None)
    continuation = models.PositiveIntegerField(_('Afhandeling'), choices=CONTINUATIONS, default=GO)

    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    date_should_end = models.DateField(blank=True, null=True)

    proposal = models.ForeignKey(Proposal)

    def update_go(self):
        """
        Check all decisions: if all are finished, set the final decision and date_end.
        """
        all_decisions = self.decision_set.count()
        closed_decisions = 0
        final_go = True
        for decision in self.decision_set.all():
            if decision.go != '':
                closed_decisions += 1
                final_go &= decision.go == Decision.APPROVED

        if all_decisions == closed_decisions:
            self.go = final_go
            self.date_end = timezone.now()
            self.save()

            # For a supervisor review:
            if self.stage == self.SUPERVISOR:
                # Update the status of the Proposal with the end date
                self.proposal.date_reviewed_supervisor = self.date_end
                self.proposal.save()
                # On GO and not in course, start the assignment phase
                if self.go and not self.proposal.in_course:
                    from .utils import start_assignment_phase
                    start_assignment_phase(self.proposal)
                # On NO-GO, reset the Proposal status
                # TODO: also send e-mail?
                else:
                    self.proposal.status = Proposal.DRAFT
                    self.proposal.save()
            # For a review by commission:
            else:
                # Set the stage to CLOSING
                self.stage = self.CLOSING
                self.save()

    def accountable_user(self):
        return self.proposal.accountable_user()

    def current_reviewers(self):
        return get_user_model().objects.filter(decision__review=self)

    def __unicode__(self):
        return u'Review of %s' % self.proposal


class Decision(models.Model):
    APPROVED = 'Y'
    NOT_APPROVED = 'N'
    NEEDS_REVISION = '?'
    APPROVAL = (
        (APPROVED, _('goedgekeurd')),
        (NOT_APPROVED, _('niet goegekeurd')),
        (NEEDS_REVISION, _('revisie noodzakelijk')),
    )

    go = models.CharField(
        _('Beslissing'),
        max_length=1,
        choices=APPROVAL,
        blank=True)
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
        return u'Decision #%d by %s on %s: %s' % (self.pk, self.reviewer.username, self.review.proposal, self.go)
