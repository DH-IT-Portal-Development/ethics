# actions allowed in list view, may be moved to utils later
def action_allowed_next_step(self):
    # if_modifiable return true
    return True


def action_allowed_show_difference(self):
    # if_modifiable return true
    return True


def action_allowed_delete(self):
    # if_modifiable return true
    return True


def action_allowed_view(self):
    # if_submitted return true
    return True


def action_allowed_make_revision(self):
    # if_submitted return true
    return True


def action_allowed_make_decision(self):
    # if_supervised return true
    return True


def action_allowed_hide(self):
    # if_secretary return true
    return True


def action_allowed_add(self):
    # if_secretary return true
    return True


from django.utils.translation import gettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

from proposals.models import Proposal
from reviews.models import Review, Decision

import datetime


class ProposalActions:  # Base Class also overlapw with ReviwActions, except the detail_actions itself.
    def __init__(self, proposal, user):
        self.proposal = proposal
        self.user = user

        # Create and initialize actions
        self.detail_actions = [
            NextStepProposalAction(proposal, user),
            #  ShowDifference(proposal, user),
            # Delete(proposal, user),
            # View(proposal, user),
            # MakeRevision(proposal, user),
            # MakeDecision(proposal, user),
            # Hide(proposal, user),
            # Add(proposal, user),
        ]
        self.ufl_actions = []

        # Does not check for uniqueness
        self.all_actions = self.ufl_actions + self.detail_actions

    def __call__(self):
        return self.get_all_actions()

    def get_all_actions(self):
        return [a for a in self.all_actions if a.is_available()]

    def get_ufl_actions(self):
        return [a for a in self.ufl_actions if a.is_available()]

    def get_detail_actions(self):
        return [a for a in self.detail_actions if a.is_available()]


class ProposalAction:  # Heavily overlaps with ReviewAction, perhaps these two can be fused.
    def __init__(self, proposal, user):
        self.proposal = proposal
        self.user = user

    def is_available(self, user=None):
        """Returns true if this action is available to the specified
        user given the current object."""

        if not user:
            user = self.user

        # Defaults to always available
        return True

    def action_url(self, user=None):
        """Returns a URL for the action"""

        if not user:
            user = self.user

        return "#"

    def text_with_link(self, user=None):
        return '<a href="{}">{}</a>'.format(
            self.action_url(),
            self.description(),
        )

    def description(self):
        return "description or name for {} not defined".format(self.__name__)

    def __str__(self):
        return mark_safe(self.text_with_link())


class NextStepProposalAction(ProposalAction):
    def is_available(self):
        """User needs to be the owner of the proposal or the superviser.
        The proposal needs to be in the right state. Draft?"""
        return True

    def action_url(self, user=None):
        return reverse("proposals:next_action", args=(self.proposal.pk,))

    def description(self):
        return _("nextactiondescription")


class HideProposalAction(ProposalAction):
    def is_available(self):
        """Only allow secretaries"""

        user = self.user

        user_groups = user.groups.values_list("name", flat=True)
        if not settings.GROUP_SECRETARY in user_groups:
            return False

        return True

    def action_url(self, user=None):
        return reverse("proposals:hide", args=(self.proposal.pk,))

    def description(self):
        return _("hideactiondescription")
