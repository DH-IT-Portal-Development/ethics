from braces.views import LoginRequiredMixin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters

from cdh.vue3.components.uu_list import UUListAPIView
from reviews.mixins import CommitteeMixin
from cdh.vue.rest import FancyListApiView

from main.utils import is_secretary
from reviews.models import Review
from .serializers import (
    ProposalSerializer,
    ProposalApiSerializer,
    SupervisedApiSerializer,
)
from ..models import Proposal


class ProposalFilterSet(filters.FilterSet):
    # TODO: my supervisod, my practice

    # can this be rewritten in lambda? If so how?
    status_choices = Proposal.Statuses.choices
    for choice in status_choices:
        if choice[0] == 60:
            status_choices.remove(choice)
    status = filters.MultipleChoiceFilter(
        label="Status",
        field_name="status",
        choices=status_choices,
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
        return Proposal.objects.filter(applicants=self.request.user)


class MySupervisedApiView(LoginRequiredMixin, UUListAPIView):
    serializer_class = SupervisedApiSerializer
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
    ordering = "date_submitted_supervisor"  # desc is removed compared to old UI, does not seem to be a thing

    def get_queryset(self):
        """Returns all Proposals supervised by the current User"""
        return Proposal.objects.filter(supervisor=self.request.user)


class BaseProposalsApiView(LoginRequiredMixin, FancyListApiView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = ProposalSerializer

    sort_definitions = [
        FancyListApiView.SortDefinition("date_submitted", _("Datum ingediend")),
        FancyListApiView.SortDefinition("date_reviewed", _("Datum afgerond")),
        FancyListApiView.SortDefinition("date_modified", _("Laatst bijgewerkt")),
    ]
    default_sort = ("date_modified", "desc")

    def get_my_proposals(self):
        return (
            Proposal.objects.filter(
                Q(applicants=self.request.user) | Q(supervisor=self.request.user)
            )
            .distinct()
            .select_related(  # this optimizes the loading a bit
                "supervisor",
                "parent",
                "relation",
                "parent__supervisor",
                "parent__relation",
            )
            .prefetch_related(
                "applicants",
                "review_set",
                "parent__review_set",
                "study_set",
                "study_set__observation",
                "study_set__session_set",
                "study_set__intervention",
                "study_set__session_set__task_set",
            )
        )

    def get_context(self):
        context = super().get_context()

        context["is_secretary"] = is_secretary(self.request.user)
        context["proposal"] = {
            "SUBMITTED_TO_SUPERVISOR": Proposal.Statuses.SUBMITTED_TO_SUPERVISOR,
            "DECISION_MADE": Proposal.Statuses.DECISION_MADE,
        }
        context["review"] = {
            "REVISION": Review.Continuations.REVISION,
        }
        context["user_pk"] = self.request.user.pk

        return context


class MyProposalsApiView(BaseProposalsApiView):
    def get_queryset(self):
        """Returns all Proposals for the current User"""
        return self.get_my_proposals()


class MyConceptsApiView(BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition("date_modified", _("Laatst bijgewerkt")),
    ]

    def get_queryset(self):
        """Returns all non-submitted Proposals for the current User"""
        return self.get_my_proposals().filter(
            status__lt=Proposal.Statuses.SUBMITTED_TO_SUPERVISOR
        )


class MySubmittedApiView(BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition("date_submitted", _("Datum ingediend")),
        FancyListApiView.SortDefinition("date_modified", _("Laatst bijgewerkt")),
    ]
    default_sort = ("date_submitted", "desc")

    def get_queryset(self):
        """Returns all submitted Proposals for the current User"""
        return self.get_my_proposals().filter(
            status__gte=Proposal.Statuses.SUBMITTED_TO_SUPERVISOR,
            status__lt=Proposal.Statuses.DECISION_MADE,
        )


class MyCompletedApiView(BaseProposalsApiView):
    def get_queryset(self):
        """Returns all completed Proposals for the current User"""
        return self.get_my_proposals().filter(
            status__gte=Proposal.Statuses.DECISION_MADE
        )


class MyPracticeApiView(BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition("date_modified", _("Laatst bijgewerkt")),
    ]

    def get_queryset(self):
        """Returns all practice Proposals for the current User"""
        return Proposal.objects.filter(
            Q(in_course=True) | Q(is_exploration=True),
            Q(applicants=self.request.user) | Q(supervisor=self.request.user),
        )


class ProposalArchiveApiView(CommitteeMixin, BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition("date_submitted", _("Datum ingediend")),
        FancyListApiView.SortDefinition("date_reviewed", _("Datum afgerond")),
    ]
    default_sort = ("date_reviewed", "desc")

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon"""
        return Proposal.objects.users_only_archive(committee=self.committee)
