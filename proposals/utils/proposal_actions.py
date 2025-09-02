from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

from proposals.models import Proposal
from reviews.models import Review, Decision

import datetime


class ProposalActions:
    # comments are from proposal_list.html in the vue_templates map, task is to verify the actions are corrrect.

    @staticmethod
    def action_allowed_view_pdf(proposal: Proposal) -> bool:
        return proposal.status >= Proposal.Statuses.SUBMITTED_TO_SUPERVISOR

    # assumes creator of proposal or supervisor of proposal
    @staticmethod
    def action_allowed_edit(proposal: Proposal) -> bool:
        return proposal.status == Proposal.Statuses.DRAFT

    # assumes creator of proposal or supervisor of proposal
    @staticmethod
    def action_allowed_delete(proposal: Proposal) -> bool:
        return proposal.status == Proposal.Statuses.DRAFT

    # if you are able to see it you have user permissions
    @staticmethod
    def action_allowed_show_difference(proposal: Proposal) -> bool:
        return proposal.is_revision

    # if you are able to see it you have user permissions
    @staticmethod
    def action_allowed_make_revision(proposal: Proposal) -> bool:
        return proposal.is_revisable

    # assumes user is supervisor && proposal.supervisor.pk matches supervisor.
    @staticmethod
    def action_allowed_make_supervise_decision(proposal: Proposal) -> bool:
        return (
            proposal.status == proposal.Statuses.SUBMITTED_TO_SUPERVISOR
            and proposal.supervisor
        )

    # assumes user is secretary
    @staticmethod
    def action_allowed_hide_from_archive(proposal: Proposal) -> bool:
        return proposal.in_archive

    @staticmethod
    def action_allowed_add_to_archive(proposal: Proposal) -> bool:
        # missing logic
        check = lambda o: o.status == Proposal.Statuses.SUBMITTED
        return check(proposal)

    # This is the original logic before DDV implementation, fairly roundabout logic that
    # matches the date_modified in all cases.
    # I propose we remove this, I have it here so you can judge if I missed something.
    @staticmethod
    def get_last_date(proposal: Proposal):
        review = proposal.latest_review()
        if review is not None:
            if (
                proposal.latest_review
                and review.continuation == Review.Continuations.REVISION
            ):
                return "Besloten op: " + str(proposal.date_reviewed.date())

        if proposal.date_confirmed:
            return "Besloten op: " + str(proposal.date_confirmed)
        else:
            return "Laatst bijgewerkt: " + str(proposal.date_modified.date())

    # this is original info but not sure where to fit this yet and if I want to add this at all.
    @staticmethod
    def route_info(proposal: Proposal):
        if (
            proposal.latest_review
        ):  # && context.wants_route_info is also here but i do not know where that comes from.
            return "Route:" + proposal.latest_review().route
        return None
