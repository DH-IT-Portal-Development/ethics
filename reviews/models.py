from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from proposals.models import Proposal


class Review(models.Model):
    class Stages(models.IntegerChoices):
        SUPERVISOR = 0, _("Beoordeling door eindverantwoordelijke")
        ASSIGNMENT = 1, _("Aanstelling commissieleden")
        COMMISSION = 2, _("Beoordeling door commissie")
        CLOSING = 3, _("Afsluiting door secretaris")
        CLOSED = 4, _("Afgesloten")

    class Continuations(models.IntegerChoices):
        GO = 0, _("Goedkeuring door FETC-GW")
        REVISION = 1, _("Revisie noodzakelijk")
        NO_GO = 2, _("Afwijzing door FETC-GW")
        LONG_ROUTE = 3, _("Open review met lange (4-weken) route")
        METC = 4, _("Laat opnieuw beoordelen door METC")
        GO_POST_HOC = 5, _("Positief advies van FETC-GW, post-hoc")
        NO_GO_POST_HOC = 6, _("Negatief advies van FETC-GW, post-hoc")
        DISCONTINUED = 7, _("Niet verder in behandeling genomen")

    stage = models.PositiveIntegerField(
        choices=Stages.choices, default=Stages.SUPERVISOR
    )
    short_route = models.BooleanField(_("Route"), default=None, null=True, blank=True)
    go = models.BooleanField(_("Beslissing"), default=None, null=True, blank=True)
    continuation = models.PositiveIntegerField(
        _("Afhandeling"),
        choices=Continuations.choices,
        default=Continuations.GO,
    )

    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    date_should_end = models.DateField(blank=True, null=True)

    is_committee_review = models.BooleanField(default=True)

    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)

    def update_go(self, last_decision=None):
        """
        Check all decisions: if all are finished, set the final decision and date_end.
        If this review is discontinued, don't do anything.
        """

        # If this review is discontinued, it is set in stone
        if self.continuation == self.Continuations.DISCONTINUED:
            return

        all_decisions = self.decision_set.count()
        closed_decisions = 0
        final_go = True
        for decision in self.decision_set.all():
            if decision.go != "":
                closed_decisions += 1
                final_go &= decision.go == Decision.Approval.APPROVED

        if all_decisions == closed_decisions:
            self.go = final_go
            self.date_end = timezone.now()
            self.save()
            # For a supervisor review:
            if self.is_committee_review is False:
                # Update the status of the Proposal with the end date
                self.proposal.date_reviewed_supervisor = self.date_end
                self.proposal.save()
                # Supervisor reviews have no CLOSING phase,
                # so they always go straight to CLOSED.
                self.stage = self.Stages.CLOSED
                self.save()
                # On GO and not in course, start the assignment phase
                if self.go and not self.proposal.in_course:
                    # Use absolute import. Relative works fine everywhere except
                    # in an uWSGI environment, in which it errors.
                    from reviews.utils import start_assignment_phase

                    start_assignment_phase(self.proposal)
                # On NO-GO, reset the Proposal status
                else:
                    # See comment above
                    from reviews.utils import notify_supervisor_nogo

                    notify_supervisor_nogo(last_decision)
                    self.proposal.status = Proposal.Statuses.DRAFT
                    self.proposal.save()
            # For a review by commission:
            else:
                # Set the stage to CLOSING
                from reviews.utils import notify_secretary_all_decisions

                notify_secretary_all_decisions(self)
                self.stage = self.Stages.CLOSING
                self.save()
        else:
            # In case there is still an unmade decision, make sure to
            # unset date end. This re-opens the review in case a new reviewer
            # is added after the first conclusion.
            self.date_end = None
            self.save()

    def get_continuation_display(self):
        # If this review hasn't concluded, this will only return 'Approved' as
        # this is the default. Thus, we return 'unknown' if we are still pre-
        # conclusion.
        if self.stage <= Review.Stages.COMMISSION:
            return _("Onbekend")

        # Get the human readable string
        continuation = self.Continuations(self.continuation).label

        if self.proposal.has_minor_revision:
            continuation += str(_(", met revisie"))

        return continuation

    def get_route_display(self):
        route_options = {
            False: _("lange (4-weken) route"),
            True: _("korte (2-weken) route"),
            None: _("nog geen route"),
        }

        return route_options[self.short_route]

    def accountable_user(self):
        return self.proposal.accountable_user()

    def get_applicant_names_emails(self):
        names_and_emails = [
            (user.get_full_name(), user.email)
            for user in self.proposal.applicants.all()
        ]
        name_email_strings = []
        for pair in names_and_emails:
            name_email_strings.append(",\n".join(pair))
        return name_email_strings

    def current_reviewers(self):
        return get_user_model().objects.filter(decision__review=self)

    def get_attachments_list(self, request=None):
        from attachments.utils import AttachmentsList

        attachments_list = AttachmentsList(
            review=self,
            request=request,
        )
        return attachments_list

    def __str__(self):
        return "Review of %s" % self.proposal


class Decision(models.Model):
    class Approval(models.TextChoices):
        APPROVED = "Y", _("goedgekeurd")
        NOT_APPROVED = "N", _("niet goedgekeurd")
        NEEDS_REVISION = "?", _("revisie noodzakelijk")

    go = models.CharField(
        _("Beslissing"), max_length=1, choices=Approval.choices, blank=True
    )

    date_decision = models.DateTimeField(blank=True, null=True)

    comments = models.TextField(_("Ruimte voor onderbouwing"), blank=True)

    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "review",
            "reviewer",
        )

    def save(self, *args, **kwargs):
        """
        Sets the correct status of the Review on save of a Decision.
        """
        super(Decision, self).save(*args, **kwargs)
        self.review.update_go(last_decision=self)

    def is_final_decision(self):
        """
        Checks if this is the final review in a reviewing round.

        Will always return True on Supervisor reviews.
        """
        open_decisions = self.review.decision_set.filter(
            go="",
        )
        return open_decisions.count() < 2

    def __str__(self):
        return "Decision #%d by %s on %s: %s" % (
            self.pk,
            self.reviewer.username,
            self.review.proposal,
            self.go,
        )
