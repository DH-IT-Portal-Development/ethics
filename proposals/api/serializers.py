from rest_framework import serializers

from main.serializers import UserSerializer
from proposals.models import Proposal
from reviews.api.serializers import InlineReviewSerializer, \
    InlineDecisionSerializer
from cdh.core.rest.serializers import ModelDisplaySerializer


class ProposalInlineSerializer(ModelDisplaySerializer):
    class Meta:
        model = Proposal
        fields = ['pk', 'reference_number', 'title', 'is_revision',
                  'type', 'date_confirmed', 'date_submitted',
                  'date_reviewed', 'date_modified', 'latest_review',
                  'supervisor_decision', 'applicants', 'status', 'supervisor',
                  'pdf', 'in_archive']

    latest_review = serializers.SerializerMethodField()
    supervisor = serializers.SerializerMethodField()
    supervisor_decision = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    pdf = serializers.SerializerMethodField()


    def get_latest_review(self, proposal):
        review = proposal.latest_review()

        if review:
            return InlineReviewSerializer(review).data

        return None

    def get_supervisor(self, proposal):
        supervisor = proposal.supervisor

        if supervisor:
            return UserSerializer(supervisor).data

        return None

    def get_supervisor_decision(self, proposal):
        decision = proposal.supervisor_decision()

        if decision:
            return InlineDecisionSerializer(decision).data

        return None

    def get_applicants(self, proposal):
        return UserSerializer(proposal.applicants.all(), many=True).data

    def get_pdf(self, proposal):
        if proposal.pdf:
            return {
                "name": proposal.pdf.name,
                "url": proposal.pdf.url,
            }

        return None


class ProposalSerializer(ProposalInlineSerializer):
    class Meta:
        model = Proposal
        fields = ['pk', 'reference_number', 'title', 'is_revision', 'type',
                  'date_confirmed', 'date_submitted',
                  'date_submitted_supervisor', 'date_reviewed', 'date_modified',
                  'parent', 'latest_review', 'supervisor_decision',
                  'applicants', 'status', 'supervisor', 'continue_url',
                  'pdf', 'in_archive']

    parent = serializers.SerializerMethodField()

    def get_parent(self, proposal):
        if proposal.parent:
            return ProposalInlineSerializer(proposal.parent).data

        return None
