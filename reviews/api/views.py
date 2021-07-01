from collections import OrderedDict
from typing import Tuple

from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import SessionAuthentication

from main.utils import is_secretary
from proposals.models import Proposal
from uil.vue.rest import FancyListApiView
from ..mixins import CommitteeMixin

from ..models import Decision, Review
from .serializers import DecisionSerializer, ReviewSerializer


class BaseDecisionApiView(GroupRequiredMixin, CommitteeMixin, FancyListApiView):
    authentication_classes = (SessionAuthentication, )
    serializer_class = DecisionSerializer
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    filter_definitions = [
        FancyListApiView.FilterDefinition(
            'review.get_stage_display',
            _("Stadium"),
        ),
        FancyListApiView.FilterDefinition(
            'review.route',
            _("Route"),
        ),
        FancyListApiView.FilterDefinition(
            'proposal.is_revision',
            _("Revisie"),
        ),
    ]

    sort_definitions = [
        FancyListApiView.SortDefinition(
            label=_('Referentienummer'),
            field='proposal.reference_number',
        ),
        FancyListApiView.SortDefinition(
            label=_('Datum ingediend'),
            field='proposal.date_submitted',
        ),
        FancyListApiView.SortDefinition(
            label=_('Start datum'),
            field='review.date_start',
        ),
    ]
    default_sort = ('proposal.date_submitted', 'desc')

    def get_context(self):
        context = super().get_context()

        context['is_secretary'] = is_secretary(self.request.user)
        context['review'] = {
            'ASSIGNMENT': Review.ASSIGNMENT,
            'COMMISSION': Review.COMMISSION,
            'CLOSING': Review.CLOSING,
            'CLOSED': Review.CLOSED,
            'GO': Review.GO,
            'GO_POST_HOC': Review.GO_POST_HOC,
        }
        context['current_user_pk'] = self.request.user.pk

        return context


class MyDecisionsApiView(BaseDecisionApiView):

    def get_default_sort(self) -> Tuple[str, str]:
        if is_secretary(self.request.user):
            return 'review.date_start', "desc"

        return 'proposal.date_submitted', "desc"

    def get_queryset(self):
        """Returns all open Decisions of the current User"""

        if is_secretary(self.request.user):
            return self.get_queryset_for_secretary()

        return self.get_queryset_for_committee()

    def get_queryset_for_committee(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()

        objects = Decision.objects.filter(
            reviewer=self.request.user,
            review__proposal__reviewing_committee=self.committee
        )

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]

    def get_queryset_for_secretary(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()
        # Decision-for-secretary-exists cache.
        dfse_cache = {}

        objects = Decision.objects.filter(
            reviewer__groups__name=settings.GROUP_SECRETARY,
            review__proposal__reviewing_committee=self.committee
        )

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal,
                    reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision isn't
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and obj.reviewer != self.request.user:
                continue

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class MyOpenDecisionsApiView(BaseDecisionApiView):

    def get_default_sort(self) -> Tuple[str, str]:
        if is_secretary(self.request.user):
            return 'review.date_start', "desc"

        return 'proposal.date_submitted', "desc"

    def get_queryset(self):
        """Returns all open Decisions of the current User"""

        if is_secretary(self.request.user):
            return self.get_queryset_for_secretary()

        return self.get_queryset_for_committee()


    def get_queryset_for_committee(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()

        objects = Decision.objects.filter(
            reviewer=self.request.user,
            go='',
            review__proposal__reviewing_committee=self.committee
        )

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]

    def get_queryset_for_secretary(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()
        # Decision-for-secretary-exists cache.
        dfse_cache = {}

        objects = Decision.objects.filter(
            reviewer__groups__name=settings.GROUP_SECRETARY,
            go='',
            review__proposal__reviewing_committee=self.committee
        )

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal,
                    reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision isn't
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and obj.reviewer != self.request.user:
                continue

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class OpenDecisionsApiView(BaseDecisionApiView):
    group_required = [
        settings.GROUP_SECRETARY,
    ]

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        decisions = OrderedDict()
        # Decision-for-secretary-exists cache.
        dfse_cache = {}

        objects = Decision.objects.filter(
            go='',
            review__proposal__reviewing_committee=self.committee
        ).exclude(review__stage=Review.SUPERVISOR)

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal,
                    reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision *is*
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and obj.reviewer == self.request.user:
                continue

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class OpenSupervisorDecisionApiView(BaseDecisionApiView):
    group_required = [
        settings.GROUP_SECRETARY,
    ]

    def get_queryset(self):
        """Returns all studies that still need to be reviewed by the secretary
        """
        objects = Decision.objects.filter(
            go='',
            review__stage=Review.SUPERVISOR,
            review__proposal__status=Proposal.SUBMITTED_TO_SUPERVISOR,
            review__proposal__reviewing_committee=self.committee
        )

        decisions = OrderedDict()

        for obj in objects:
            proposal = obj.review.proposal
            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class BaseReviewApiView(GroupRequiredMixin, CommitteeMixin, FancyListApiView):
    authentication_classes = (SessionAuthentication, )
    serializer_class = ReviewSerializer

    filter_definitions = [
        FancyListApiView.FilterDefinition(
            'get_stage_display',
            _("Stadium"),
        ),
        FancyListApiView.FilterDefinition(
            'route',
            _("Route"),
        ),
        FancyListApiView.FilterDefinition(
            'proposal.is_revision',
            _("Revisie"),
        ),
        FancyListApiView.FilterDefinition(
            'get_continuation_display',
            _('Afhandeling'),
        ),
    ]

    sort_definitions = [
        FancyListApiView.SortDefinition(
            label=_('Referentienummer'),
            field='proposal.reference_number',
        ),
        FancyListApiView.SortDefinition(
            label=_('Datum ingediend'),
            field='proposal.date_submitted',
        ),
        FancyListApiView.SortDefinition(
            label=_('Start datum'),
            field='date_start',
        ),
    ]
    default_sort = ('proposal.date_submitted', 'desc')

    def get_context(self):
        context = super().get_context()

        context['is_secretary'] = is_secretary(self.request.user)
        context['review'] = {
            'ASSIGNMENT': Review.ASSIGNMENT,
            'COMMISSION': Review.COMMISSION,
            'CLOSING': Review.CLOSING,
            'CLOSED': Review.CLOSED,
            'GO': Review.GO,
            'GO_POST_HOC': Review.GO_POST_HOC,
        }
        context['current_user_pk'] = self.request.user.pk

        return context


class ToConcludeReviewApiView(BaseReviewApiView):
    group_required = settings.GROUP_SECRETARY

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        reviews = {}
        objects = Review.objects.filter(
            stage__gte=Review.CLOSING,
            proposal__status__gte=Proposal.SUBMITTED,
            proposal__date_confirmed=None,
            proposal__reviewing_committee=self.committee,
        ).filter(
            Q(continuation=Review.GO) |
            Q(continuation=Review.GO_POST_HOC) |
            Q(continuation=None)
        ).select_related(
            'proposal',
            "proposal__parent",
            'proposal__created_by',
            'proposal__supervisor',
            'proposal__relation',
        ).prefetch_related(
            'proposal__review_set',
            'proposal__applicants',
            'decision_set',
            'decision_set__reviewer'
        )

        for obj in objects:
            proposal = obj.proposal
            if proposal.pk not in reviews:
                reviews[proposal.pk] = obj
            else:
                if reviews[proposal.pk].pk < obj.pk:
                    reviews[proposal.pk] = obj

        return [value for key, value in reviews.items()]


class AllReviewsApiView(BaseReviewApiView):
    default_sort = ('date_start', 'desc')

    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group

        group_required = [settings.GROUP_SECRETARY]

        if self.committee.name == 'AK':
            group_required += [settings.GROUP_GENERAL_CHAMBER]
        if self.committee.name == 'LK':
            group_required += [settings.GROUP_LINGUISTICS_CHAMBER]

        return group_required

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        reviews = OrderedDict()
        objects = Review.objects.filter(
            stage__gte=Review.ASSIGNMENT,
            proposal__status__gte=Proposal.SUBMITTED,
            proposal__reviewing_committee=self.committee,
        ).select_related(
            'proposal',
            "proposal__parent",
            'proposal__created_by',
            'proposal__supervisor',
            'proposal__relation',
        ).prefetch_related(
            'proposal__review_set',
            'proposal__applicants',
            'decision_set',
            'decision_set__reviewer'
        )

        for obj in objects:
            proposal = obj.proposal
            if proposal.pk not in reviews:
                reviews[proposal.pk] = obj
            else:
                if reviews[proposal.pk].pk < obj.pk:
                    reviews[proposal.pk] = obj

        return [value for key, value in reviews.items()]
