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


class ProposalActionsSerializer(ModelDisplaySerializer):
    # A small DDV explanation:
    # link_attr= variable in the model. For example proposal.pk is used in action_view_pdf.
    # the lambda function which we give also uses the model object parameter
    # which is otherwise not available as far as I can see. That is why we have function inside a lambda function
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

    action_go_to_next_step = DDVLinkField(
        text=_("Naar volgende stap"),
        link="proposals:update",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_go_to_next_step(proposal),
    )

    action_delete = DDVLinkField(
        text=_("Verwijderen"),
        link="proposals:delete",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_delete(proposal),
    )

    action_make_revision = DDVLinkField(
        text=_("Maak revisie"),
        link="proposals:copy",  # there is also a copy revison and copy amendment,
        # not sure when those two are supposed to be shown
        check=lambda proposal: ProposalActions.action_allowed_make_revision(proposal),
    )

    action_make_decision = DDVLinkField(
        text=_("Aanvraag beoordelen"),
        link="reviews:decide",  # there is also a decide new in urls, what is the differnce?
        link_attr="pk",  # wrong pk, I need the pk of the review that is linke to the proposal
        check=lambda proposal: ProposalActions.action_allowed_make_supervise_decision(
            proposal
        ),
    )

    # DDVActionsField description is inaccurate, there always need to be at least one option.
    my_proposal_actions = DDVActionsField(
        [
            action_view_pdf_always_available,  # placeholder until solution found, so likely a permanent solution.
            action_show_difference,
            action_go_to_next_step,
            action_delete,
            action_make_revision,
        ]
    )

    my_supervised_actions = DDVActionsField(
        [
            action_view_pdf_always_available,
            action_show_difference,
            action_go_to_next_step,
            action_make_decision,
        ]
    )


class ProposalApiSerializer(ProposalActionsSerializer):
    class Meta:
        model = Proposal
        fields = [
            "reference_number",
            "pk",  # pk is temp, easier to implement right now, not needed otherwise.
            "title",
            "type",
            "date_modified",
            "date_submitted",
            "state_or_decision",
            "usernames",
            "my_proposal_actions",
        ]

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
    def get_usernames(proposal: Proposal):
        return proposal.get_applicants_names()

    # I have no idea where the old logic is, so I had to make it anew. It does not seem to be in proposal.
    # This logic should not stay in the serialiser but for now it works.
    @staticmethod
    def get_state_or_decision(proposal: Proposal):
        # should proposal.supervisor_decision be here?

        # how do I test the WMO_decison made?
        if proposal.status == (
            Proposal.Statuses.DECISION_MADE or Proposal.Statuses.WMO_DECISION_MADE
        ):
            return proposal.latest_review.get_continuation_display()
        else:
            return proposal.get_status_display()
            # get_status_display() does not exist in proposal, why this still works:
            # https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.get_FOO_display


class SupervisedApiSerializer(ProposalApiSerializer):
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
            "date_submitted_supervisor",
            "date_reviewed_supervisor",
            "my_supervised_actions",
        ]
