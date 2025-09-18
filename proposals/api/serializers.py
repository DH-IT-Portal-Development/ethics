from main.serializers import UserSerializer
from proposals.models import Proposal
from reviews.api.serializers import InlineReviewSerializer, InlineDecisionSerializer
from cdh.rest.server.serializers import ModelDisplaySerializer
from rest_framework import (
    serializers,
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
