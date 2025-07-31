from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

from proposals.models import Proposal
from reviews.models import Review, Decision

import datetime

# actiontree, implementation in proosal_actions.py
"""
    {% if modifiable %}
        <img src="{{ img_next }}" title="Naar volgende stap">
        <img src="{{ img_diff }}" title="Toon verschillen">
        <img src="{{ img_delete }}" title="Verwijderen">
     {% if submitted %} #this also somehow shows the state, not status, and submitted is a status
        <img src="{{ img_pdf }}" title="Inzien">
        <img src="{{ img_revise }}" title="Maak revisie">
      {% if supervised %}
          <img src="{{ img_decide }}" title="Beslissen">
       {% if is_secretary %}
             <img src="{{ img_hide }}" title="Verbergen">
               <img src="{{ img_add }}" title="Toevoegen">

"""


class ProposalActions:
    # Needs to give a callable function to serializers. Either with a function or a __call__. Not sure what
    # works best yet

    # the serializer does not have acces to user, but these functions without a user variable are weird as well.
    # user validation may also not be the responsibility of a serializer, in that case supervised and normal view
    # still need to be separate.

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
    def action_allowed_view_pdf(proposal: Proposal):
        # if_submitted return true
        # does seem to be always available, why is there a submitted requirement?
        return proposal.status == Proposal.Statuses.SUBMITTED

    # This should be moved to Review Actions later on. The decision is about a Review
    # though it has a proposal parameter right now so still unsure.
    # also there already seems to a methid in review actions but not sure how to convert that to something the serializer can read yet

    # for supervizedview later
    # actions_make_decision = DDVLinkField(
    # text="decide",
    # link="reviews:decide",
    #  link_attr="latest_review_pk",  # This shows a review pk but an incorrect one.
    #   check=lambda proposal: ProposalActions.action_allowed_make_decision(proposal),
    # )
    @staticmethod
    def action_allowed_make_decision(proposal: Proposal):
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
