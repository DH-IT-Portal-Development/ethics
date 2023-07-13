from braces.views import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from rest_framework.authentication import SessionAuthentication

from reviews.mixins import CommitteeMixin
from uil.vue.rest import FancyListApiView

from main.utils import is_secretary
from reviews.models import Review
from .serializers import ProposalSerializer
from ..models import Proposal


class BaseProposalsApiView(LoginRequiredMixin, FancyListApiView):
    authentication_classes = (SessionAuthentication, )
    serializer_class = ProposalSerializer

    sort_definitions = [
        FancyListApiView.SortDefinition(
            'date_submitted',
            _('Datum ingediend')
        ),
        FancyListApiView.SortDefinition(
            'date_reviewed',
            _('Datum afgerond')
        ),
        FancyListApiView.SortDefinition(
            'date_modified',
            _('Laatst bijgewerkt')
        ),
    ]
    default_sort = ('date_modified', 'desc')

    def get_my_proposals(self):
        return Proposal.objects.filter(
            Q(applicants=self.request.user) | Q(supervisor=self.request.user)
        ).distinct().select_related(  # this optimizes the loading a bit
            'supervisor', 'parent', 'relation',
            'parent__supervisor', 'parent__relation',
        ).prefetch_related(
            'applicants', 'review_set', 'parent__review_set', 'study_set',
            'study_set__observation', 'study_set__session_set',
            'study_set__intervention', 'study_set__session_set__task_set'
        )

    def get_context(self):
        context = super().get_context()

        context['is_secretary'] = is_secretary(self.request.user)
        context['proposal'] = {
            'SUBMITTED_TO_SUPERVISOR': Proposal.SUBMITTED_TO_SUPERVISOR,
            'DECISION_MADE': Proposal.DECISION_MADE,
        }
        context['review'] = {
            'REVISION': Review.REVISION,
        }
        context['user_pk'] = self.request.user.pk

        return context


class MyProposalsApiView(BaseProposalsApiView):

    def get_queryset(self):
        """Returns all Proposals for the current User"""
        return self.get_my_proposals()


class MyConceptsApiView(BaseProposalsApiView):

    sort_definitions = [
        FancyListApiView.SortDefinition(
            'date_modified',
            _('Laatst bijgewerkt')
        ),
    ]

    def get_queryset(self):
        """Returns all non-submitted Proposals for the current User"""
        return self.get_my_proposals().filter(
            status__lt=Proposal.SUBMITTED_TO_SUPERVISOR
        )


class MySubmittedApiView(BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition(
            'date_submitted',
            _('Datum ingediend')
        ),
        FancyListApiView.SortDefinition(
            'date_modified',
            _('Laatst bijgewerkt')
        ),
    ]
    default_sort = ('date_submitted', 'desc')

    def get_queryset(self):
        """Returns all submitted Proposals for the current User"""
        return self.get_my_proposals().filter(
            status__gte=Proposal.SUBMITTED_TO_SUPERVISOR,
            status__lt=Proposal.DECISION_MADE
        )


class MyCompletedApiView(BaseProposalsApiView):

    def get_queryset(self):
        """Returns all completed Proposals for the current User"""
        return self.get_my_proposals().filter(
            status__gte=Proposal.DECISION_MADE
        )


class MySupervisedApiView(BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition(
            'date_submitted',
            _('Datum ingediend')
        ),
        FancyListApiView.SortDefinition(
            'date_submitted_supervisor',
            _('Datum ingediend bij eindverantwoordelijke')
        ),
        FancyListApiView.SortDefinition(
            'date_reviewed',
            _('Datum afgerond')
        ),
        FancyListApiView.SortDefinition(
            'date_modified',
            _('Laatst bijgewerkt')
        ),
    ]
    default_sort = ('date_submitted_supervisor', 'desc')

    def get_context(self):
        context = super().get_context()
        context['wants_route_info'] = True
        return context

    def get_queryset(self):
        """Returns all Proposals supervised by the current User"""
        return Proposal.objects.filter(
            supervisor=self.request.user
        )


class MyPracticeApiView(BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition(
            'date_modified',
            _('Laatst bijgewerkt')
        ),
    ]

    def get_queryset(self):
        """Returns all practice Proposals for the current User"""
        return Proposal.objects.filter(
            Q(in_course=True) | Q(is_exploration=True),
            Q(applicants=self.request.user) |
            Q(supervisor=self.request.user)
        )


class ProposalArchiveApiView(CommitteeMixin, BaseProposalsApiView):
    sort_definitions = [
        FancyListApiView.SortDefinition(
            'date_submitted',
            _('Datum ingediend')
        ),
        FancyListApiView.SortDefinition(
            'date_reviewed',
            _('Datum afgerond')
        ),
    ]
    default_sort = ('date_reviewed', 'desc')

    @method_decorator(cache_page(60 * 60 * 4))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon"""
        return Proposal.archived_proposals.filter(
                                       is_pre_assessment=False,
                                       reviewing_committee=self.committee,
                                       public=True).select_related(
            # this optimizes the loading a bit
            'supervisor', 'parent', 'relation',
            'parent__supervisor', 'parent__relation',
        ).prefetch_related(
            'applicants', 'review_set', 'parent__review_set', 'study_set',
            'study_set__observation', 'study_set__session_set',
            'study_set__intervention', 'study_set__session_set__task_set'
        )
