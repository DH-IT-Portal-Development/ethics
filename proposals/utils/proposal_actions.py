from django.utils.translation import gettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

from proposals.models import Proposal
from reviews.models import Review, Decision

import datetime


class ProposalActions:
    # Needs to give a callable function to serializers. Either with a function or a __call__. Not sure what
    # works best yet
    # Base Class also overlapw with ReviwActions, except the detail_actions itself.

    @staticmethod
    def action_allowed_go_to_next_step(proposal: Proposal):
        # if_modifiable return true
        return proposal.status == Proposal.Statuses.DRAFT

    # to do
    @staticmethod
    def action_allowed_show_difference(proposal: Proposal):
        # if_modifiable return true
        check = lambda o: o.status == Proposal.Statuses.DRAFT
        return check(proposal)

    @staticmethod
    def action_allowed_delete(proposal: Proposal):
        # if_modifiable return true
        return proposal.status == Proposal.Statuses.DRAFT
        # as of now should be same check as action_allowed_go_to_next_step

    @staticmethod
    def action_allowed_make_revision(proposal: Proposal):
        # if_submitted return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)

    @staticmethod
    def action_allowed_view(proposal: Proposal):
        # if_submitted return true
        return True

    # This should be moved to Review Actions later on. The decision is about a Review
    # though it has a proposal parameter right now.
    @staticmethod
    def action_allowed_make_decision(proposal: Proposal):
        # if_supervised return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED_TO_SUPERVISOR
        return check(proposal)

    @staticmethod
    def action_allowed_hide(proposal: Proposal):
        # if_secretary return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)

    @staticmethod
    def action_allowed_add(proposal: Proposal):
        # if_secretary return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)
