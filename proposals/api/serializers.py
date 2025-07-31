from rest_framework import serializers

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


class MyArchiveSerializer(ModelDisplaySerializer):
    class Meta:
        model = Proposal
        fields = [
            "reference_number",
            "title",
            "type",
            "date_submitted",
            "date_reviewed",
            "usernames",
            "state",
            "action_view_pdf",
            "action_show_difference",
            "action_go_to_next_step",
            "action_delete",
            "action_make_revision",
            "actions",
        ]

    state = serializers.SerializerMethodField()
    usernames = serializers.SerializerMethodField()

    # A small DDV explanation:
    # link_attr= variable in the model. For example proposal.pk is used in action_view_pdf.
    # Not the pdf pk. They do happen to be the same though.
    # the lambda function which we give also uses the model object parameter which is otherwise not available, I think
    action_view_pdf = DDVLinkField(
        text="pdf",
        link="proposals:pdf",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_view_pdf(proposal),
    )

    action_show_difference = DDVLinkField(
        text="show difference",
        link="proposals:diff",
        link_attr="pk",  # needs more then one pk, not sure how to do this
        check=lambda proposal: ProposalActions.action_allowed_show_difference(proposal),
    )

    action_go_to_next_step = DDVLinkField(  # different then edit?
        text="next step",
        link="proposals:update",  # this is correct, so what is the edit option?
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_go_to_next_step(proposal),
    )

    action_delete = DDVLinkField(
        text="delete",
        link="proposals:delete",
        link_attr="pk",
        check=lambda proposal: ProposalActions.action_allowed_delete(proposal),
    )

    action_make_revision = DDVLinkField(
        text="Maak revisie",
        link="proposals:copy",  # there is also a copy revison and copy amendment,
        # not sure when they are supposed to be shown
        check=lambda proposal: ProposalActions.action_allowed_make_revision(proposal),
    )

    actions = DDVActionsField(
        [
            action_go_to_next_step,
            DDVLinkField(
                text="delete",
                link="proposals:delete",
                link_attr="pk",
                check=lambda proposal: ProposalActions.action_allowed_delete(proposal),
            ),
        ]
    )

    @staticmethod
    def get_usernames(proposal: Proposal):
        # haven´t found out how to do this differently. get_applicants is the orignal but
        # I just needs the username here while get_applicants returns a user json.
        # ideally the fullname from userserializer is called with the many option but i have not found out how to do so
        # any suggestions are welcome, for now this gives the desired result, it's just very ugly
        users = ""
        for user in proposal.applicants.all():
            if users != "":
                users += ", "
            users += user.first_name + " " + user.last_name
        return users

    @staticmethod
    def get_state(proposal: Proposal):
        # state = status with decisions added so this is still lacking
        return proposal.get_status_display()
        # get_status_display() does not exist in proposal, why this still works:
        # https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.get_FOO_display
