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
        return proposal.status == Proposal.Statuses.DRAFT

    @staticmethod
    def action_allowed_show_difference(proposal: Proposal):
        if proposal.is_revision:
            return True
        return False

    @staticmethod
    def action_allowed_delete(proposal: Proposal):
        return proposal.status == Proposal.Statuses.DRAFT

    @staticmethod
    def action_allowed_make_revision(proposal: Proposal):
        return proposal.is_revisable

    @staticmethod
    def action_allowed_view_pdf(proposal: Proposal):
        return proposal.status == Proposal.Statuses.SUBMITTED

    @staticmethod
    def action_allowed_make_supervise_decision(proposal: Proposal):
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED_TO_SUPERVISOR
        return check(proposal)

    @staticmethod
    def action_allowed_hide_from_archive(proposal: Proposal):
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)

    @staticmethod
    def action_allowed_add_to_archive(proposal: Proposal):
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)
