import collections
from collections import OrderedDict
from typing import Tuple

from braces.views import GroupRequiredMixin
from django.conf import settings
from django.db.models import Q, Exists, OuterRef, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication

from main.utils import is_secretary
from proposals.models import Proposal
from cdh.vue.rest import FancyListApiView
from ..mixins import CommitteeMixin

from ..models import Decision, Review
from .serializers import DecisionSerializer, ReviewSerializer


def return_latest_decisions(decisions: QuerySet[Decision]) -> list[Decision]:
    """
    filters decisions with duplicate proposals to only give back the most recent decision for each proposal
    """
    filtered_decisions: OrderedDict[int, Decision] = (
        OrderedDict()
    )  # proposal.pk, decision
    for decision in decisions:
        proposal = decision.review.proposal
        if proposal.pk not in filtered_decisions:
            filtered_decisions[proposal.pk] = decision
        else:
            if filtered_decisions[proposal.pk].pk < decision.pk:
                filtered_decisions[proposal.pk] = decision
    return [value for key, value in filtered_decisions.items()]


# would be the same method as return_lasted_decisions if we give proposals instead of objects to this method.
def return_latest_reviews(objects):
    reviews = OrderedDict()
    for obj in objects:
        proposal = obj.proposal
        if proposal.pk not in reviews:
            reviews[proposal.pk] = obj
        else:
            if reviews[proposal.pk].pk < obj.pk:
                reviews[proposal.pk] = obj
    return reviews


class BaseDecisionApiView(GroupRequiredMixin, CommitteeMixin, FancyListApiView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = DecisionSerializer
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_CHAIR,
        settings.GROUP_PO,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    filter_definitions = [
        FancyListApiView.FilterDefinition(
            "review.get_stage_display",
            _("Stadium"),
        ),
        FancyListApiView.FilterDefinition(
            "review.route",
            _("Route"),
        ),
        FancyListApiView.FilterDefinition(
            "proposal.is_revision",
            _("Revisie"),
        ),
    ]

    sort_definitions = [
        FancyListApiView.SortDefinition(
            label=_("Referentienummer"),
            field="proposal.reference_number",
        ),
        FancyListApiView.SortDefinition(
            label=_("Datum ingediend"),
            field="proposal.date_submitted",
        ),
        FancyListApiView.SortDefinition(
            label=_("Start datum"),
            field="review.date_start",
        ),
    ]
    default_sort = ("proposal.date_submitted", "desc")

    def get_context(self):
        context = super().get_context()

        context["is_secretary"] = is_secretary(self.request.user)
        context["review"] = {
            "ASSIGNMENT": Review.Stages.ASSIGNMENT,
            "COMMISSION": Review.Stages.COMMISSION,
            "CLOSING": Review.Stages.CLOSING,
            "CLOSED": Review.Stages.CLOSED,
            "GO": Review.Continuations.GO,
            "GO_POST_HOC": Review.Continuations.GO_POST_HOC,
        }
        context["current_user_pk"] = self.request.user.pk

        return context

    def filter_decisions(self, decision_queryset: QuerySet[Decision]) -> list[Decision]:
        """
        filters decisions with duplicate proposals to only give back the most recent decision for each proposal
        also makes sure the decisions are for this user.
        """
        filtered_decisions: OrderedDict[int, Decision] = (
            OrderedDict()
        )  # proposal.pk, decision
        # Decision-for-secretary-exists cache.
        dfse_cache: dict[int, bool] = (
            {}
        )  # proposal.pk, decision for reviewer exists on current proposal

        for decision in decision_queryset:
            proposal = decision.review.proposal

            # add proposal to dfse if not yet in it
            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal, reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision isn't
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk]:
                if decision.reviewer != self.request.user:
                    continue

            if proposal.pk not in filtered_decisions:
                filtered_decisions[proposal.pk] = decision
            else:
                if filtered_decisions[proposal.pk].pk < decision.pk:
                    filtered_decisions[proposal.pk] = decision

        decisions: list[Decision] = [value for key, value in filtered_decisions.items()]
        return decisions


class MyDecisionsApiView(BaseDecisionApiView):
    def get_default_sort(self) -> Tuple[str, str]:
        if is_secretary(self.request.user):
            return "review.date_start", "desc"

        return "proposal.date_submitted", "desc"

    def get_queryset(self):
        """Returns all open Decisions of the current User"""

        if is_secretary(self.request.user):
            return self.get_queryset_for_secretary()

        return self.get_queryset_for_committee()

    def get_queryset_for_committee(self):
        """Returns all open Decisions of the current User"""

        decision_queryset = Decision.objects.filter(
            reviewer=self.request.user,
            review__proposal__reviewing_committee=self.committee,
            review__continuation__lt=Review.Continuations.DISCONTINUED,
            review__is_committee_review=True,
        )

        decisions: list[Decision] = return_latest_decisions(decision_queryset)

        return [value for key, value in decisions.items()]

    def get_queryset_for_secretary(self):
        """Returns all open Decisions of the current User"""

        decision_queryset = Decision.objects.filter(
            reviewer__groups__name=settings.GROUP_SECRETARY,
            review__proposal__reviewing_committee=self.committee,
            review__continuation__lt=Review.Continuations.DISCONTINUED,
            review__is_committee_review=True,
        )

        return self.filter_decisions(decision_queryset)


class MyOpenDecisionsApiView(BaseDecisionApiView):
    def get_default_sort(self) -> Tuple[str, str]:
        if is_secretary(self.request.user):
            return "review.date_start", "desc"

        return "proposal.date_submitted", "desc"

    def get_queryset(self):
        """Returns all open Decisions of the current User"""

        if is_secretary(self.request.user):
            return self.get_queryset_for_secretary()

        return self.get_queryset_for_committee()

    def get_queryset_for_committee(self):
        """Returns all open Decisions of the current User"""

        objects = Decision.objects.filter(
            reviewer=self.request.user,
            go="",
            review__proposal__reviewing_committee=self.committee,
            review__continuation__lt=Review.Continuations.DISCONTINUED,
            review__is_committee_review=True,
        )

        decisions: list[Decision] = return_latest_decisions(objects)
        return decisions

    def get_queryset_for_secretary(self):
        """Returns all open Decisions of the current User"""

        decision_queryset: QuerySet[Decision] = Decision.objects.filter(
            reviewer__groups__name=settings.GROUP_SECRETARY,
            go="",
            review__proposal__reviewing_committee=self.committee,
            review__continuation__lt=Review.Continuations.DISCONTINUED,
            review__is_committee_review=True,
        )
        return self.filter_decisions(decision_queryset)


class OpenDecisionsApiView(BaseDecisionApiView):
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_CHAIR,
        settings.GROUP_PO,
    ]

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""

        decision_queryset = Decision.objects.filter(
            go="",
            review__proposal__reviewing_committee=self.committee,
            review__continuation__lt=Review.Continuations.DISCONTINUED,
            review__is_committee_review=True,
        )

        filtered_decisions: OrderedDict[int, Decision] = (
            OrderedDict()
        )  # proposal.pk, decision
        # Decision-for-secretary-exists cache.
        dfse_cache: dict[int, bool] = {}  # proposal.pk, proposal exists

        for decision in decision_queryset:
            proposal = decision.review.proposal

            # add proposal to dfse if not yet in it
            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal, reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision *is*
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and decision.reviewer == self.request.user:
                continue

            if proposal.pk not in filtered_decisions:
                filtered_decisions[proposal.pk] = decision
            else:
                if filtered_decisions[proposal.pk].pk < decision.pk:
                    filtered_decisions[proposal.pk] = decision

        decisions: list[Decision] = [value for key, value in filtered_decisions.items()]
        return decisions


class OpenSupervisorDecisionApiView(BaseDecisionApiView):
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_CHAIR,
        settings.GROUP_PO,
    ]

    sort_definitions = [
        FancyListApiView.SortDefinition(
            label=_("Referentienummer"),
            field="proposal.reference_number",
        ),
        FancyListApiView.SortDefinition(
            label=_("Datum ingediend"),
            field="proposal.date_submitted_supervisor",
        ),
        FancyListApiView.SortDefinition(
            label=_("Start datum"),
            field="review.date_start",
        ),
    ]
    default_sort = ("proposal.date_submitted_supervisor", "desc")

    def get_queryset(self):
        """Returns all proposals that still need to be reviewed by the supervisor"""
        objects = Decision.objects.filter(
            go="",
            review__proposal__reviewing_committee=self.committee,
            review__stage=Review.Stages.SUPERVISOR,
            review__proposal__status=Proposal.Statuses.SUBMITTED_TO_SUPERVISOR,
        )

        decisions: list[Decision] = return_latest_decisions(objects)
        return decisions


class BaseReviewApiView(GroupRequiredMixin, CommitteeMixin, FancyListApiView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = ReviewSerializer

    filter_definitions = [
        FancyListApiView.FilterDefinition(
            "get_stage_display",
            _("Stadium"),
        ),
        FancyListApiView.FilterDefinition(
            "route",
            _("Route"),
        ),
        FancyListApiView.FilterDefinition(
            "proposal.is_revision",
            _("Revisie"),
        ),
        FancyListApiView.FilterDefinition(
            "get_continuation_display",
            _("Afhandeling"),
        ),
    ]

    sort_definitions = [
        FancyListApiView.SortDefinition(
            label=_("Referentienummer"),
            field="proposal.reference_number",
        ),
        FancyListApiView.SortDefinition(
            label=_("Datum ingediend"),
            field="proposal.date_submitted",
        ),
        FancyListApiView.SortDefinition(
            label=_("Start datum"),
            field="date_start",
        ),
    ]
    default_sort = ("proposal.date_submitted", "desc")

    def get_context(self):
        context = super().get_context()

        context["is_secretary"] = is_secretary(self.request.user)
        context["review"] = {
            "ASSIGNMENT": Review.Stages.ASSIGNMENT,
            "COMMISSION": Review.Stages.COMMISSION,
            "CLOSING": Review.Stages.CLOSING,
            "CLOSED": Review.Stages.CLOSED,
            "GO": Review.Continuations.GO,
            "GO_POST_HOC": Review.Continuations.GO_POST_HOC,
            "REVISION": Review.Continuations.REVISION,
        }
        context["current_user_pk"] = self.request.user.pk

        return context


class ToConcludeReviewApiView(BaseReviewApiView):
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_CHAIR,
        settings.GROUP_PO,
    ]

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        objects = (
            Review.objects.filter(
                stage__gte=Review.Stages.CLOSING,
                is_committee_review=True,
                proposal__status__gte=Proposal.Statuses.SUBMITTED,
                proposal__date_confirmed=None,
                proposal__reviewing_committee=self.committee,
            )
            .filter(
                Q(continuation=Review.Continuations.GO)
                | Q(continuation=Review.Continuations.GO_POST_HOC)
                | Q(continuation=None)
            )
            .select_related(
                "proposal",
                "proposal__parent",
                "proposal__created_by",
                "proposal__supervisor",
                "proposal__relation",
            )
            .prefetch_related(
                "proposal__review_set",
                "proposal__applicants",
                "decision_set",
                "decision_set__reviewer",
            )
        )
        reviews = return_latest_reviews(objects)

        return [value for key, value in reviews.items()]


class InRevisionApiView(BaseReviewApiView):
    """Return reviews for proposals which have been sent back for revision,
    but for which a revision has not yet been submitted"""

    default_sort = ("date_start", "desc")
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_CHAIR,
        settings.GROUP_PO,
    ]

    def get_queryset(self):
        # 1. Find reviews of revisions:
        # A revision not having a review means
        # that the review of its parent is "in revision"
        revision_reviews = Review.objects.filter(
            proposal__is_revision=True,  # Not a copy
            stage__gte=Review.Stages.ASSIGNMENT,  # Not a supervisor review
            is_committee_review=True,
        )
        # 2. Get candidate reviews:
        # All reviews whose conclusion is "revision necessary"
        # that are in the current committee
        candidates = Review.objects.filter(
            proposal__reviewing_committee=self.committee,
            stage=Review.Stages.CLOSED,
            continuation=Review.Continuations.REVISION,
            is_committee_review=True,
        )
        # 3. Finally, exclude candidates whose proposal
        # has a child with a revision review
        in_revision = candidates.exclude(
            Exists(
                revision_reviews.filter(
                    # OuterRef refers to the candidate being evaluated
                    proposal__parent__pk=OuterRef("proposal__pk")
                )
            )
        )
        return in_revision


class AllOpenReviewsApiView(BaseReviewApiView):
    default_sort = ("date_start", "desc")

    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group

        group_required = [
            settings.GROUP_SECRETARY,
            settings.GROUP_CHAIR,
            settings.GROUP_PO,
        ]
        settings.GROUP_PO,

        if self.committee.name == "AK":
            group_required += [settings.GROUP_GENERAL_CHAMBER]
        if self.committee.name == "LK":
            group_required += [settings.GROUP_LINGUISTICS_CHAMBER]

        return group_required

    def get_queryset(self):
        """Returns all open Reviews"""

        objects = (
            Review.objects.filter(
                stage__gte=Review.Stages.ASSIGNMENT,
                stage__lte=Review.Stages.CLOSING,
                proposal__status__gte=Proposal.Statuses.SUBMITTED,
                proposal__reviewing_committee=self.committee,
            )
            .select_related(
                "proposal",
                "proposal__parent",
                "proposal__created_by",
                "proposal__supervisor",
                "proposal__relation",
            )
            .prefetch_related(
                "proposal__review_set",
                "proposal__applicants",
                "decision_set",
                "decision_set__reviewer",
            )
        )
        reviews = return_latest_reviews(objects)

        return [value for key, value in reviews.items()]


class AllReviewsApiView(BaseReviewApiView):
    default_sort = ("date_start", "desc")

    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group

        group_required = [
            settings.GROUP_SECRETARY,
            settings.GROUP_CHAIR,
            settings.GROUP_PO,
        ]

        if self.committee.name == "AK":
            group_required += [settings.GROUP_GENERAL_CHAMBER]
        if self.committee.name == "LK":
            group_required += [settings.GROUP_LINGUISTICS_CHAMBER]

        return group_required

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        objects = (
            Review.objects.filter(
                stage__gte=Review.Stages.ASSIGNMENT,
                proposal__status__gte=Proposal.Statuses.SUBMITTED,
                proposal__reviewing_committee=self.committee,
                is_committee_review=True,
            )
            .select_related(
                "proposal",
                "proposal__parent",
                "proposal__created_by",
                "proposal__supervisor",
                "proposal__relation",
            )
            .prefetch_related(
                "proposal__review_set",
                "proposal__applicants",
                "decision_set",
                "decision_set__reviewer",
            )
        )
        reviews = return_latest_reviews(objects)

        return [value for key, value in reviews.items()]
