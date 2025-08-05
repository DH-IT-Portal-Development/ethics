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
     {% if submitted %} 
        <img src="{{ img_pdf }}" title="Inzien">
        <img src="{{ img_revise }}" title="Maak revisie">
      {% if supervised %}
          <img src="{{ img_decide }}" title="Beslissen">
       {% if is_secretary %}
             <img src="{{ img_hide }}" title="Verbergen">
               <img src="{{ img_add }}" title="Toevoegen">
"""


# Does not check user permissions as of now
class ProposalActions:
    is_modifiable = False  # should be true when DRAFT OR (supervised & submitted), no access to supervision from serializer.

    # Needs to give a callable function to serializers. Either with a function or a __call__. Not sure what
    # works best yet

    # the serializer does not have acces to user, but these functions without a user variable are weird as well.
    # user validation may also not be the responsibility of a serializer, in that case supervised and normal view
    # still need to be separate.

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
