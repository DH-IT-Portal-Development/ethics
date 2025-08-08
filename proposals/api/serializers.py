from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from main.serializers import UserSerializer, UserMinimalSerializer
from proposals.models import Proposal
from proposals.utils.proposal_actions import ProposalActions
from reviews.api.serializers import InlineReviewSerializer, InlineDecisionSerializer
from cdh.rest.server.serializers import ModelDisplaySerializer
from rest_framework import (
    serializers,
)  # am I allowed to do this or should this go through cdh?
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

    @staticmethod
    def get_supervisor(proposal):
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
            "reference_number",
            "title",
            "is_revision",
            "type",
            "date_confirmed",
            "date_submitted",
            "date_submitted_supervisor",
            "date_reviewed",
            "date_modified",
            "parent",
            "latest_review",
            "supervisor_decision",
            "applicants",
            "status",
            "supervisor",
            "continue_url",
            "pdf",
            "in_archive",
            "is_revisable",
        ]

    parent = serializers.SerializerMethodField()

    @staticmethod
    def get_parent(proposal):
        if proposal.parent:
            return ProposalInlineSerializer(proposal.parent).data

        return None


class DDVProposalSerializer(ModelDisplaySerializer):
    """DDVProposalSerializer does not implement the Meta class,
    a requirement since this class inherits ModelDisplaySerializer"""

    # A small DDV explanation:
    # link_attr= variable in the model. For example proposal.pk is used in action_view_pdf.
    # the lambda function which we give also uses the model object parameter
    # which is otherwise not available as far as I can see.
    action_view_pdf = DDVLinkField(
        text=_("Inzien"),
        link="proposals:pdf",
        link_attr="pk",
        new_tab=True,
        check=lambda proposal: ProposalActions.action_allowed_view_pdf(proposal),
    )

    action_view_pdf_always_available = DDVLinkField(
        text=_("Inzien"),
        link="proposals:pdf",
        link_attr="pk",
        new_tab=True,
    )

    action_show_difference = DDVLinkField(
        text=_("Toon Verschillen"),
        link="proposals:diff",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_show_difference(proposal),
    )

    action_edit = DDVLinkField(
        text=_("Naar volgende stap"),
        link="proposals:update",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_edit(proposal),
    )

    action_delete_separator = DDVActionDividerField(
        check=lambda proposal: ProposalActions.action_allowed_delete(proposal),
    )

    action_delete = DDVLinkField(
        text=_("Verwijderen"),
        link="proposals:delete",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_delete(proposal),
    )

    action_make_revision = DDVLinkField(
        text=_("Maak revisie"),
        link="proposals:copy",
        check=lambda proposal: ProposalActions.action_allowed_make_revision(proposal),
    )

    action_make_decision = DDVLinkField(
        text=_("Aanvraag beoordelen"),
        link="reviews:decide",
        link_attr="supervisor_decision_pk",
        check=lambda proposal: ProposalActions.action_allowed_make_supervise_decision(
            proposal
        ),
    )

    # DDVActionsField description is inaccurate, there always need to be at least one option.
    # action_view_pdf_always_available can be used as placeholder until solution found, so likely a permanent solution.
    my_proposal_actions = DDVActionsField(
        [
            action_view_pdf_always_available,
            action_show_difference,
            action_edit,
            action_make_revision,
            action_delete_separator,
            action_delete,
        ]
    )

    my_supervised_actions = DDVActionsField(
        [
            action_view_pdf_always_available,
            action_show_difference,
            action_edit,
            action_make_decision,
            action_delete_separator,
            action_delete,
        ]
    )

    date_modified = serializers.SerializerMethodField()
    date_submitted = serializers.SerializerMethodField()
    state_or_decision = serializers.SerializerMethodField()
    usernames = serializers.SerializerMethodField()

    # DDVDate returns 1970 by default so we have to use a DDVString and format the date ourselves
    # incoming format: 2025-04-24T11:59:45.583305+02:00
    @staticmethod
    def get_date_modified(proposal: Proposal):
        if proposal.date_modified is not None:
            return proposal.date_modified.date()
        return ""

    @staticmethod
    def get_date_submitted(proposal: Proposal):
        if proposal.date_submitted is not None:
            return proposal.date_submitted.date()
        return ""

    @staticmethod
    def get_state_or_decision(proposal: Proposal):
        if proposal.status == (
            Proposal.Statuses.DECISION_MADE or Proposal.Statuses.WMO_DECISION_MADE
        ):
            return proposal.latest_review().get_continuation_display()
        else:
            return proposal.get_status_display()
            # get_status_display() does not exist in proposal, why this still works:
            # https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.get_FOO_display

    @staticmethod
    def get_usernames(proposal: Proposal) -> str:
        return proposal.get_applicants_names()


class ProposalApiSerializer(DDVProposalSerializer):
    class Meta:
        model = Proposal
        fields = [
            "reference_number",
            "title",
            "type",
            "date_modified",
            "date_submitted",
            "state_or_decision",
            "usernames",
            "my_proposal_actions",
        ]


class SupervisedApiSerializer(DDVProposalSerializer):
    class Meta:
        model = Proposal
        fields = [
            "reference_number",
            "title",
            "type",
            "date_modified",
            "date_submitted",
            "state_or_decision",
            "usernames",
            "info",
            "my_supervised_actions",
        ]

    info = serializers.SerializerMethodField()

    @staticmethod
    def get_info(proposal: Proposal) -> str:
        review = proposal.latest_review()
        if review is not None:
            return review.get_stage_display()
        return ""
