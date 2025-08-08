from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

from proposals.models import Proposal
from reviews.models import Review, Decision

import datetime


class ProposalActions:

    @staticmethod
    def action_allowed_edit(proposal: Proposal):
        # if_modifiable return true
        return proposal.status == Proposal.Statuses.DRAFT

    @staticmethod
    def action_allowed_show_difference(proposal: Proposal):
        # if_modifiable return true
        if proposal.is_revision:  # amendment_or_revision is also an option?
            return True
        return False

    @staticmethod
    def action_allowed_delete(proposal: Proposal):
        # if_modifiable return true
        return proposal.status == Proposal.Statuses.DRAFT
        # as of now should be same check as action_allowed_go_to_next_step

    @staticmethod
    def action_allowed_make_revision(proposal: Proposal):
        # if_submitted return true
        return proposal.is_revisable

    @staticmethod
    def action_allowed_view_pdf(proposal: Proposal):
        # if_submitted return true
        # does seem to be always available, why is there a submitted requirement?
        return proposal.status == Proposal.Statuses.SUBMITTED

    # This should be moved to Review Actions later on. The decision is about a Review
    # though it has a proposal parameter right now so still unsure.
    # also there already seems to a method in review actions but not sure how to convert that to something the serializer can read yet

    @staticmethod
    def action_allowed_make_supervise_decision(proposal: Proposal):
        # if_supervised return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED_TO_SUPERVISOR
        return check(proposal)

    # hid and add to archive may not belong here, but I will not remove them without confirmation that they do not belong
    # in a proposal view.
    @staticmethod
    def action_allowed_hide_from_archive(proposal: Proposal):
        # if_secretary return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)

    @staticmethod
    def action_allowed_add_to_archive(proposal: Proposal):
        # if_secretary return true
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)
