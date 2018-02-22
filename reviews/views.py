from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views import generic

from braces.views import LoginRequiredMixin, GroupRequiredMixin

from core.utils import get_secretary, get_reviewers
from proposals.models import Proposal

from .forms import ReviewAssignForm, ReviewCloseForm, DecisionForm
from .mixins import UserAllowedMixin, AutoReviewMixin
from .models import Review, Decision
from .utils import start_review_route, notify_secretary


class DecisionListView(GroupRequiredMixin, generic.ListView):
    context_object_name = 'decisions'
    group_required = [settings.GROUP_SECRETARY, settings.GROUP_COMMISSION]

    def get_queryset(self):
        """Returns all Decisions of the current User"""
        return Decision.objects.filter(reviewer=self.request.user)


class DecisionMyOpenView(GroupRequiredMixin, generic.ListView):
    context_object_name = 'decisions'
    group_required = [settings.GROUP_SECRETARY, settings.GROUP_COMMISSION]

    def get_queryset(self):
        """Returns all open Decisions of the current User"""
        return Decision.objects.filter(reviewer=self.request.user, go='')


class DecisionOpenView(GroupRequiredMixin, generic.ListView):
    context_object_name = 'decisions'
    template_name = 'reviews/decision_list_open.html'
    group_required = settings.GROUP_SECRETARY

    def get_queryset(self):
        """Returns all open Decisions of all Users"""
        return Decision.objects.filter(go='')


class SupervisorView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all the current open Decisions for the current User"""
        return Decision.objects.filter(review__date_end=None, review__stage=Review.SUPERVISOR, reviewer=self.request.user)


class ReviewDetailView(LoginRequiredMixin, AutoReviewMixin, UserAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review


class ReviewAssignView(GroupRequiredMixin, AutoReviewMixin, generic.UpdateView):
    """
    Allows a User of the SECRETARY group to assign reviewers.
    """
    model = Review
    form_class = ReviewAssignForm
    template_name = 'reviews/review_assign_form.html'
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        return reverse('reviews:my_open')

    def form_valid(self, form):
        """Updates the Review stage and start the selected Review route for the selected Users."""
        route = form.instance.short_route
        review = self.object

        if route is not None:
            # Start a short/long route
            form.instance.stage = Review.COMMISSION

            current_reviewers = set(review.current_reviewers())
            selected_reviewers = set(form.cleaned_data['reviewers'])
            new_reviewers = selected_reviewers - current_reviewers
            obsolete_reviewers = current_reviewers - selected_reviewers - {get_secretary()}

            # Create a new Decision for new reviewers
            start_review_route(form.instance, new_reviewers, route)

            # Remove the Decision for obsolete reviewers
            Decision.objects.filter(review=review, reviewer__in=obsolete_reviewers).delete()
        else:
            # Directly mark this Proposal as closed: applicants should start a revision Proposal
            for decision in Decision.objects.filter(review=review):
                decision.go = Decision.NEEDS_REVISION
                decision.date_decision = timezone.now()
                decision.save()

            form.instance.continuation = Review.REVISION
            form.instance.date_end = timezone.now()
            form.instance.stage = Review.CLOSED

        return super(ReviewAssignView, self).form_valid(form)


class ReviewCloseView(GroupRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewCloseForm
    template_name = 'reviews/review_close_form.html'
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        return reverse('reviews:my_archive')

    def get_form_kwargs(self):
        """
        Adds allow_long_route_continuation to the form_kwargs.
        The long route continuation is only allowed for short route Reviews
        that are not of preliminary assessment Proposals.
        """
        review = self.get_object()

        kwargs = super(ReviewCloseView, self).get_form_kwargs()
        kwargs['allow_long_route_continuation'] = review.short_route and not review.proposal.is_pre_assessment
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
        initial['in_archive'] = not review.proposal.is_pre_assessment
        return initial

    def form_valid(self, form):
        proposal = form.instance.proposal

        if form.instance.continuation in [Review.GO, Review.NO_GO]:
            proposal.status = Proposal.DECISION_MADE
            proposal.status_review = form.instance.continuation == Review.GO
            proposal.date_reviewed = timezone.now()
            proposal.save()
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
            proposal.status = Proposal.DRAFT
            proposal.save()
            proposal.wmo.enforced_by_commission = True
            proposal.wmo.save()

        proposal.in_archive = form.cleaned_data['in_archive']
        proposal.save()

        form.instance.stage = Review.CLOSED

        return super(ReviewCloseView, self).form_valid(form)


class DecisionUpdateView(LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """
    Allows a User to make a Decision on a Review.
    """
    model = Decision
    form_class = DecisionForm

    def is_reviewer(self):
        if self.request.user.is_superuser:
            return True
        user_groups = self.request.user.groups.values_list("name", flat=True)
        return {settings.GROUP_SECRETARY, settings.GROUP_COMMISSION}.intersection(set(user_groups))

    def get_success_url(self):
        if self.is_reviewer():
            return reverse('reviews:my_archive')
        else:
            return reverse('proposals:my_archive')

    def form_valid(self, form):
        """Save the decision date and send e-mail to secretary"""
        form.instance.date_decision = timezone.now()
        notify_secretary(form.instance)
        return super(DecisionUpdateView, self).form_valid(form)
