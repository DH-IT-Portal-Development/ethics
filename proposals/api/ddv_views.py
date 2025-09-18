from braces.views import LoginRequiredMixin
from cdh.vue3.components.uu_list import UUListAPIView
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter

from proposals.api.ddv_serializers import ProposalApiSerializer, SupervisedApiSerializer
from proposals.models import Proposal


class ProposalFilterSet(filters.FilterSet):

    # WMO_Decision_made is no longer in use.
    status = filters.MultipleChoiceFilter(
        label="Status",
        field_name="status",
        choices=[
            choice
            for choice in Proposal.Statuses.choices
            if choice[0] != Proposal.Statuses.WMO_DECISION_MADE.value
        ],
    )


class ProposalApiView(LoginRequiredMixin, UUListAPIView):
    serializer_class = ProposalApiSerializer
    filter_backends = [OrderingFilter, SearchFilter, filters.DjangoFilterBackend]
    filterset_class = ProposalFilterSet
    search_fields = [
        "title",
        "reference_number",
        "supervisor__first_name",
        "supervisor__last_name",
        "applicants__first_name",
        "applicants__last_name",
    ]
    ordering_fields = [
        "reference_number",
        "date_submitted",
        "date_modified",
    ]
    ordering = ["-date_modified"]

    def get_queryset(self):
        return Proposal.objects.filter(
            Q(applicants=self.request.user),
            Q(in_course=False) & Q(is_exploration=False),
        )


class MyPracticeApiView(ProposalApiView):
    """Gets all practise applications including supervisor."""

    # practise proposals for supervisor currently do appear in MySupervised instead of in practise.
    def get_queryset(self):
        """Returns all practice Proposals for the current User"""
        return Proposal.objects.filter(
            Q(in_course=True) | Q(is_exploration=True),
            Q(applicants=self.request.user) | Q(supervisor=self.request.user),
        )


class MySupervisedApiView(ProposalApiView):
    serializer_class = SupervisedApiSerializer
    ordering_fields = [
        "reference_number",
        "date_submitted",
        "date_modified",
        "date_submitted_supervisor",
    ]
    ordering = "date_submitted_supervisor"

    def get_queryset(self):
        """Returns all Proposals supervised by the current User"""
        return Proposal.objects.filter(supervisor=self.request.user)
