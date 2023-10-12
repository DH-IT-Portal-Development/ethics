from datetime import date, timedelta

from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q, Count

from main.utils import get_reviewers, get_secretary
from proposals.models import Proposal
from .forms import (DecisionForm, ReviewAssignForm, ReviewCloseForm,
                    ChangeChamberForm, ReviewDiscontinueForm, StartEndDateForm)
from .mixins import (AutoReviewMixin, UserAllowedMixin,
                     CommitteeMixin,
                     UsersOrGroupsAllowedMixin)
from .models import Decision, Review
from .utils.review_utils import notify_secretary, start_review_route, \
                                 discontinue_review, assign_reviewers
from .utils.review_actions import ReviewActions


class BaseDecisionListView(GroupRequiredMixin, CommitteeMixin, generic.TemplateView):
    template_name = 'reviews/ufl_list.html'
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['list_template'] = "reviews/vue_templates/decision_list.html"

        return context
    
class DecisionListView(BaseDecisionListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Mijn besluiten")
        context['data_url'] = reverse(
            "reviews:api:my_archive",
            args=[self.committee]
        )

        return context


class DecisionMyOpenView(BaseDecisionListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Mijn openstaande besluiten")
        context['data_url'] = reverse(
            "reviews:api:my_open",
            args=[self.committee]
        )

        return context


class DecisionOpenView(BaseDecisionListView):
    group_required = settings.GROUP_SECRETARY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Openstaande besluiten commissieleden")
        context['list_template'] = "reviews/vue_templates/decision_list_reviewer.html"
        context['data_url'] = reverse("reviews:api:open", args=[self.committee])

        return context
    

class CommitteeMembersWorkloadView(GroupRequiredMixin, CommitteeMixin, generic.FormView):
    
    template_name = 'reviews/committee_members_workload.html'
    group_required = [settings.GROUP_SECRETARY]
    form_class = StartEndDateForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_end_date = date.today()
        self.default_start_date = self.default_end_date - timedelta(days=365)

    def get_initial(self):
        initial = super().get_initial()

        if 'start_date' in self.request.GET and 'end_date' in self.request.GET:
            initial['start_date'] = self.request.GET.get('start_date')
            initial['end_date'] = self.request.GET.get('end_date')            
        else:
            initial['start_date'] = self.default_start_date
            initial['end_date'] = self.default_end_date

        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['decisions'] = self.get_all_open_decisions()
        context['today'] = date.today()
        context['reviewers'] = self.get_review_counts_last_year()

        return context

    def get_committee_decisions(self):

        decisions = Decision.objects.filter(
            review__proposal__reviewing_committee = self.committee
        ).select_related(
            'reviewer',
            'review',
            'review__proposal',
        )
        return decisions

    def get_all_open_decisions(self):
        '''Returns a queryset with all open decisions'''

        open_decisions = self.get_committee_decisions().filter(
            review__stage = Review.COMMISSION,
            ).order_by(
            "reviewer",
            "review__date_start"
            )

        return open_decisions
   
    def get_review_counts_last_year(self):
        '''This function returns an annoted queryset, with counts
        for specific review types, per reviewer.'''

        decisions = self.get_committee_decisions()
        dates = self.get_initial()

        reviewers = get_user_model().objects.filter(decision__in = decisions) 
        base_filter = Q(
            decision__review__date_start__gt=dates['start_date'],
            decision__review__date_start__lt=dates['end_date'],
            decision__review__stage__gt=Review.SUPERVISOR,
        )
        return reviewers.annotate(
            total=Count("decision", filter=base_filter),
            num_short_route=Count("decision", filter=base_filter & Q(
                decision__review__proposal__is_revision=False,
                decision__review__short_route=True
            )),
            num_long_route=Count("decision", filter=base_filter & Q(
                decision__review__proposal__is_revision=False,
                decision__review__short_route=False
            )),
            num_revision=Count("decision", filter=base_filter & Q(
                decision__review__proposal__is_revision=True
            )),
        )


class SupervisorDecisionOpenView(BaseDecisionListView):
    """
    This page displays all proposals to be reviewed by supervisors.
    """
    group_required = settings.GROUP_SECRETARY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Openstaande besluiten eindverantwoordelijken")
        context['list_template'] = "reviews/vue_templates/decision_list_reviewer.html"
        context['data_url'] = reverse(
            "reviews:api:open_supervisors",
            args=[self.committee]
        )

        return context


class BaseReviewListView(GroupRequiredMixin, CommitteeMixin, generic.TemplateView):
    template_name = 'reviews/ufl_list.html'
    group_required = [
        settings.GROUP_SECRETARY,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['list_template'] = "reviews/vue_templates/review_list.html"

        return context


class ToConcludeProposalView(BaseReviewListView):
    group_required = settings.GROUP_SECRETARY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Nog af te handelen aanvragen")
        context['data_url'] = reverse(
            "reviews:api:to_conclude",
            args=[self.committee]
        )

        return context


class InRevisionReviewsView(BaseReviewListView):

    group_required = [settings.GROUP_SECRETARY]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Aanvragen in revisie")
        context['data_url'] = reverse(
            "reviews:api:in_revision",
            args=[self.committee],
            )
        return context



class AllOpenProposalReviewsView(BaseReviewListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Alle lopende aanvragen")
        context['data_url'] = reverse(
            "reviews:api:all_open",
            args=[self.committee]
        )

        return context

    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group

        group_required = [settings.GROUP_SECRETARY]

        if self.committee.name == 'AK':
            group_required += [ settings.GROUP_GENERAL_CHAMBER ]
        if self.committee.name == 'LK':
            group_required += [ settings.GROUP_LINGUISTICS_CHAMBER ]

        return group_required


class AllProposalReviewsView(BaseReviewListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Alle ingezonden aanvragen")
        context['data_url'] = reverse(
            "reviews:api:archive",
            args=[self.committee]
        )

        return context

    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group

        group_required = [settings.GROUP_SECRETARY]

        if self.committee.name == 'AK':
            group_required += [ settings.GROUP_GENERAL_CHAMBER ]
        if self.committee.name == 'LK':
            group_required += [ settings.GROUP_LINGUISTICS_CHAMBER ]

        return group_required


class ReviewDetailView(LoginRequiredMixin, AutoReviewMixin,
                       UsersOrGroupsAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review

    def get_group_required(self):

        obj = self.get_object()
        group_required = [ settings.GROUP_SECRETARY, obj.proposal.reviewing_committee.name ]

        return group_required


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        actions = ReviewActions(self.object, user=self.request.user)
        context['detail_actions'] = actions.get_detail_actions()

        return context




class ChangeChamberView(LoginRequiredMixin, UserAllowedMixin,
                        generic.UpdateView):
    model = Proposal
    form_class = ChangeChamberForm
    template_name = 'reviews/change_chamber_form.html'

    def get_success_url(self):
        committee = self.object.reviewing_committee.name
        return reverse('reviews:detail', args=[self.object.latest_review().pk])


class ReviewAssignView(GroupRequiredMixin, AutoReviewMixin, generic.UpdateView):
    """
    Allows a User of the SECRETARY group to assign reviewers.
    """
    model = Review
    form_class = ReviewAssignForm
    template_name = 'reviews/review_assign_form.html'
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        return reverse('reviews:detail', args=[self.object.pk])

    def form_valid(self, form):
        """Updates the Review stage and start the selected Review route for the selected Users."""
        route = form.instance.short_route
        review = self.object
        selected_reviewers = set(form.cleaned_data['reviewers'])

        if route is not None:
            # Start a short/long route or reassign reviewers
            assign_reviewers(review, selected_reviewers, route)

        else:
            # Directly mark this Proposal as closed: applicants should start a revision Proposal
            for decision in Decision.objects.filter(review=review):
                decision.go = Decision.NEEDS_REVISION
                decision.date_decision = timezone.now()
                decision.save()

            # Mark the proposal as finished
            proposal = form.instance.proposal
            proposal.status = Proposal.DECISION_MADE
            proposal.status_review = False
            proposal.date_reviewed = timezone.now()
            proposal.save()

            form.instance.continuation = Review.REVISION
            form.instance.date_end = timezone.now()
            form.instance.stage = Review.CLOSED

        return super(ReviewAssignView, self).form_valid(form)


class ReviewDiscontinueView(GroupRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewDiscontinueForm
    template_name = 'reviews/review_discontinue_form.html'
    group_required = settings.GROUP_SECRETARY

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        review = self.get_object()

        if review.continuation in [review.DISCONTINUED,
                                   review.GO,
                                   review.GO_POST_HOC,
                                   ]:
            return HttpResponseRedirect(self.get_success_url())

        return super().dispatch(
            request, *args, **kwargs
        )

    def get_success_url(self):
        'Return to the detail view after unsubmission'
        return reverse('reviews:detail', args=[self.get_object().pk])

    def form_valid(self, form):
        'Sets the discontinued continuation on the review'
        review = form.instance
        discontinue_review(review)

        return super().form_valid(form)



class ReviewCloseView(GroupRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewCloseForm
    template_name = 'reviews/review_close_form.html'
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        return reverse('reviews:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        """
        Adds allow_long_route_continuation to the form_kwargs.
        The long route continuation is only allowed for short route Reviews
        that are not of preliminary assessment Proposals.
        """
        review = self.get_object()

        kwargs = super(ReviewCloseView, self).get_form_kwargs()
        kwargs[
            'allow_long_route_continuation'] = review.short_route and not review.proposal.is_pre_assessment
        return kwargs

    def get_initial(self):
        """
        Set initial values:
        - continuation to GO if review was positive
        - in_archive to True as long as we are not dealing with preliminary assessment
        """
        review = self.get_object()

        initial = super(ReviewCloseView, self).get_initial()
        initial['continuation'] = Review.GO if review.go else Review.NO_GO

        if review.proposal.date_start and \
           review.proposal.date_start < date.today():
            initial['continuation'] = \
                Review.GO_POST_HOC if initial['continuation'] == Review.GO \
                else Review.NO_GO_POST_HOC

        initial['in_archive'] = not review.proposal.is_pre_assessment
        return initial

    def form_valid(self, form):
        proposal = form.instance.proposal

        if form.instance.continuation in [
                Review.GO,
                Review.NO_GO,
                Review.GO_POST_HOC,
                Review.NO_GO_POST_HOC,
                Review.REVISION,
        ]:
            proposal.mark_reviewed(form.instance.continuation)
        elif form.instance.continuation == Review.LONG_ROUTE:
            # Create a new review
            review = Review.objects.create(
                proposal=proposal,
                stage=Review.COMMISSION,
                short_route=False,
                date_start=timezone.now())
            # Create a Decision for the secretary
            Decision.objects.create(review=review, reviewer=get_secretary())
            # Start the long review route
            start_review_route(review, get_reviewers(), False)
        elif form.instance.continuation == Review.METC:
            proposal.enforce_wmo()

        proposal.in_archive = form.cleaned_data['in_archive']
        proposal.has_minor_revision = form.cleaned_data['has_minor_revision']
        proposal.minor_revision_description = form.cleaned_data[
            'minor_revision_description']
        proposal.save()

        form.instance.stage = Review.CLOSED

        return super(ReviewCloseView, self).form_valid(form)


class CreateDecisionRedirectView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 generic.RedirectView):
    """
    This redirect first creates a new decision for a secretary that does not
    have one yet, and redirects to the DecisionUpdateView.

    NOTE: this view has been removed from templates to allow for multiple
    secretaries to work without them unnecessarily creating decisions. It
    might be of use again in the future, but for now the FEtC-H has decided
    to no longer require a secretary decision for every review. See PR
    #188 for details.
    """
    group_required = settings.GROUP_SECRETARY

    def get_redirect_url(self, *args, **kwargs):
        review_pk = kwargs.get('review', None)
        decision_pk = None

        if not review_pk:
            raise PermissionDenied

        existing_decision_qs = Decision.objects.filter(
            reviewer=self.request.user,
            review_id=review_pk
        )

        # Re-use an existing one if present
        if existing_decision_qs.exists():
            decision_pk = existing_decision_qs.last()
        else:
            decision = Decision.objects.create(
                reviewer=self.request.user,
                review_id=review_pk,
            )
            decision_pk = decision.pk

        return reverse('reviews:decide', args=[decision_pk])


class DecisionUpdateView(LoginRequiredMixin, UserAllowedMixin,
                         generic.UpdateView):
    """
    Allows a User to make a Decision on a Review.
    """
    model = Decision
    form_class = DecisionForm

    def is_reviewer(self):
        if self.request.user.is_superuser:
            return True
        user_groups = self.request.user.groups.values_list("name", flat=True)
        return {settings.GROUP_SECRETARY, settings.GROUP_LINGUISTICS_CHAMBER,
                settings.GROUP_GENERAL_CHAMBER
        }.intersection(set(user_groups))

    def get_success_url(self):
        if self.is_reviewer():
            committee = self.object.review.proposal.reviewing_committee.name
            return reverse('reviews:detail', args=[self.object.review.pk])
        else:
            return reverse('proposals:my_archive')

    def form_valid(self, form):
        """Save the decision date and send e-mail to secretary"""
        form.instance.date_decision = timezone.now()
        review = form.instance.review

        # Don't notify the secretary if this is a supervisor decision.
        # If it was a GO they the secretary will be notified anyway
        if not review.stage == review.SUPERVISOR:
            notify_secretary(form.instance)

        return super(DecisionUpdateView, self).form_valid(form)
