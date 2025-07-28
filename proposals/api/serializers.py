from rest_framework import serializers

from main.serializers import UserSerializer, UserMinimalSerializer
from proposals.models import Proposal
from proposals.utils.proposal_actions import ProposalActions, NextStepProposalAction
from reviews.api.serializers import InlineReviewSerializer, InlineDecisionSerializer
from cdh.rest.server.serializers import ModelDisplaySerializer
from cdh.vue3.components.uu_list import (
    DDVLinkField,
    DDVActionsField,
    DDVActionDividerField,
)


class ProposalInlineSerializer(ModelDisplaySerializer):
    class Meta:
        model = Proposal
        fields = [
            "pk",
            "reference_number",
            "title",
            "is_revision",
            "type",
            "date_confirmed",
            "date_submitted",
            "date_reviewed",
            "date_modified",
            "latest_review",
            "supervisor_decision",
            "applicants",
            "status",
            "supervisor",
            "pdf",
            "in_archive",
        ]

    latest_review = serializers.SerializerMethodField()
    supervisor = serializers.SerializerMethodField()
    supervisor_decision = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    pdf = serializers.SerializerMethodField()

    @staticmethod
    def get_latest_review(proposal):
        review = proposal.latest_review()

        if review:
            return InlineReviewSerializer(review).data

        return None

    def get_supervisor(self, proposal):
        supervisor = proposal.supervisor

        if supervisor:
            return UserSerializer(supervisor).data

        return None

    @staticmethod
    def get_supervisor_decision(proposal):
        decision = proposal.supervisor_decision()

        if decision:
            return InlineDecisionSerializer(decision).data

        return None

    @staticmethod
    def get_applicants(proposal):
        return UserSerializer(proposal.applicants.all(), many=True).data

    @staticmethod
    def get_pdf(proposal):
        if proposal.pdf:
            return {
                "name": proposal.pdf.name,
                "url": proposal.pdf.url,
            }
        return None


class ProposalSerializer(ProposalInlineSerializer):
    class Meta:
        model = Proposal
        fields = [
            "pk",
            "reference_number",  # used in MyProposalsView
            "title",  # used in MyProposalsView
            "is_revision",
            "type",  # used in MyProposalsView
            "date_confirmed",
            "date_submitted",  # used in MyProposalsView
            "date_submitted_supervisor",
            "date_reviewed",  # used in MyProposalsView
            "date_modified",
            "parent",
            "latest_review",
            "supervisor_decision",
            "applicants",  # used in MyProposalsView
            "status",  # used in MyProposalsView
            "supervisor",
            "continue_url",
            "pdf",  # used in MyProposalsView
            "in_archive",
            "is_revisable",
        ]

    parent = serializers.SerializerMethodField()

    @staticmethod
    def get_parent(proposal):
        if proposal.parent:
            return ProposalInlineSerializer(proposal.parent).data

        return None


class MyArchiveSerializer(ProposalInlineSerializer):
    class Meta:
        model = Proposal
        fields = [
            "reference_number",
            "title",
            "type",
            "date_submitted",
            "date_reviewed",
            "applicants",
            "state",
            "action_view_pdf",
            "action_delete",
            "action_create_revision",
            "actions_edit",
            "actions_decide",
            "actions_hide",
            "actions_show",
            "action_go_to_next_step",
            "action_show_difference",
            "actions",
        ]

    state = serializers.SerializerMethodField()

    action_go_to_next_step = DDVLinkField(
        text="pdf",
        link="http://127.0.0.1:8000/proposals/pdf/",
        link_attr="pk",
        check=lambda o: o.status != Proposal.Statuses.DRAFT,
    )
    action_view_pdf = DDVLinkField(
        text="pdf",
        link="http://127.0.0.1:8000/proposals/pdf/",
        link_attr="pk",
        check=lambda o: o.status != Proposal.Statuses.DRAFT,
    )

    action_show_difference = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.DECISION_MADE,
    )

    action_delete = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.DRAFT,
    )

    action_create_revision = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.DECISION_MADE,
    )

    actions_edit = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.SUBMITTED_TO_SUPERVISOR,
    )
    actions_decide = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.SUBMITTED_TO_SUPERVISOR,
    )
    actions_hide = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.SUBMITTED,
    )
    actions_show = DDVLinkField(
        text="Maak revisie",
        link="http://127.0.0.1:8000/proposals/copy/",
        check=lambda o: o.status == Proposal.Statuses.SUBMITTED,
    )

    actions = DDVActionsField(
        [
            DDVLinkField(
                text="Maak revisie",
                link="http://127.0.0.1:8000/proposals/copy/",
                check=lambda o: o.status == Proposal.Statuses.DECISION_MADE,
            ),
            DDVLinkField(
                text="Edit",
                link="http://127.0.0.1:8000/proposals/copy/",
                check=lambda o: o.status == Proposal.Statuses.DRAFT,
            ),
        ]
    )

    @staticmethod
    # overrides method from ProposalInlineSerializer
    def get_applicants(proposal: Proposal):
        return UserMinimalSerializer(proposal.applicants.all(), many=True).data

    @staticmethod
    def get_state(proposal: Proposal):
        # state = status with decisions added so this is still lacking
        return proposal.get_status_display()
        # get_status_display() does not exist in proposal, still works:
        # https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.get_FOO_display


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
