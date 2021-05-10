from proposals.models import Proposal
from uil.core.rest.serializers import ModelDisplaySerializer
from ..models import Decision, Review
from rest_framework import serializers
from main.serializers import UserSerializer


class ReviewProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['pk', 'reference_number', 'title', 'is_revision',
                  'date_confirmed', 'date_submitted', 'parent', 'latest_review',
                  'applicants', 'pdf']

    parent = serializers.SerializerMethodField()
    latest_review = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    pdf = serializers.SerializerMethodField()

    def get_parent(self, proposal):
        if proposal.parent:
            return ReviewProposalSerializer(proposal.parent).data

        return None

    def get_latest_review(self, proposal):
        review = proposal.latest_review()

        if review:
            return InlineReviewSerializer(review).data

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


class InlineDecisionSerializer(ModelDisplaySerializer):
    class Meta:
        model = Decision
        fields = ['pk', 'go', 'date_decision', 'comments', 'reviewer']

    reviewer = serializers.SerializerMethodField()

    def get_reviewer(self, decision):
        return UserSerializer(decision.reviewer).data


class InlineReviewSerializer(ModelDisplaySerializer):
    class Meta:
        model = Review
        fields = ['pk', 'stage', 'route', 'go', 'continuation', 'date_start',
                  'date_end', 'date_should_end', 'accountable_user',
                  'current_reviewers']

    route = serializers.CharField(source='get_route_display')
    accountable_user = serializers.SerializerMethodField()
    current_reviewers = serializers.SerializerMethodField()

    def get_accountable_user(self, review):
        return UserSerializer(review.accountable_user()).data

    def get_current_reviewers(self, review):
        return [user.pk for user in review.current_reviewers()]


class ReviewSerializer(InlineReviewSerializer):
    class Meta:
        model = Review
        fields = ['pk', 'stage', 'route', 'go', 'continuation', 'date_start',
                  'date_end', 'date_should_end', 'accountable_user', 'decision',
                  'proposal']

    decision = serializers.SerializerMethodField()
    proposal = serializers.SerializerMethodField()

    def get_decision(self, review):
        return InlineDecisionSerializer(
            review.decision_set.all(),
            many=True
        ).data

    def get_proposal(self, review):
        return ReviewProposalSerializer(review.proposal).data


class DecisionSerializer(InlineDecisionSerializer):
    class Meta:
        model = Decision
        fields = ['pk', 'go', 'date_decision', 'comments', 'review', 'reviewer',
                  'proposal']

    review = serializers.SerializerMethodField()
    proposal = serializers.SerializerMethodField()

    def get_review(self, decision):
        return InlineReviewSerializer(decision.review).data

    def get_proposal(self, decision):
        return ReviewProposalSerializer(decision.review.proposal).data

