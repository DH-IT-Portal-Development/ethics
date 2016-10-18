from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views import generic

from braces.views import LoginRequiredMixin

from core.utils import get_secretary, get_reviewers
from proposals.models import Proposal

from .forms import ReviewAssignForm, ReviewCloseForm, DecisionForm
from .mixins import UserAllowedMixin, AutoReviewMixin
from .models import Review, Decision
from .utils import start_review_route


class DecisionListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all Decisions of the current User"""
        return Decision.objects.filter(reviewer=self.request.user)


class DecisionOpenListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all open Decisions of the current User"""
        return Decision.objects.filter(reviewer=self.request.user, go=None)


class SupervisorView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all the current open Decisions for the current User"""
        return Decision.objects.filter(review__date_end=None, review__stage=Review.SUPERVISOR, reviewer=self.request.user)


class CommissionView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all the current open Decisions for the current User"""
        return Decision.objects.all()  # filter(review__date_end=None, review__stage=Review.COMMISSION, reviewer=self.request.user)


class ReviewDetailView(LoginRequiredMixin, AutoReviewMixin, UserAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review


class ReviewAssignView(LoginRequiredMixin, AutoReviewMixin, UserAllowedMixin, generic.UpdateView):
    """
    Allows a User of the SECRETARY group to assign reviewers.
    """
    model = Review
    form_class = ReviewAssignForm
    template_name = 'reviews/review_assign_form.html'

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Updates the Review stage and start the selected Review route for the selected Users."""
        form.instance.stage = Review.COMMISSION

        review = self.object
        current_reviewers = set(review.current_reviewers())
        selected_reviewers = set(form.cleaned_data['reviewers'])
        new_reviewers = selected_reviewers - current_reviewers
        obsolete_reviewers = current_reviewers - selected_reviewers - {get_secretary()}

        # Create a new Decision for new reviewers
        start_review_route(form.instance, new_reviewers, form.instance.short_route)

        # Remove the Decision for obsolete reviewers
        Decision.objects.filter(review=review, reviewer__in=obsolete_reviewers).delete()

        return super(ReviewAssignView, self).form_valid(form)


class ReviewCloseView(LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    model = Review
    form_class = ReviewCloseForm
    template_name = 'reviews/review_close_form.html'

    def get_success_url(self):
        return reverse('reviews:home')

    def get_form_kwargs(self):
        kwargs = super(ReviewCloseView, self).get_form_kwargs()
        kwargs['short_route'] = self.get_object().short_route
        return kwargs

    def get_initial(self):
        initial = super(ReviewCloseView, self).get_initial()
        initial['continuation'] = Review.GO if self.get_object().go else Review.NO_GO
        return initial

    def form_valid(self, form):
        proposal = form.instance.proposal

        if form.instance.continuation in [Review.GO, Review.NO_GO]:
            proposal.status = Proposal.DECISION_MADE
            proposal.status_review = form.instance.continuation == Review.GO
            proposal.date_reviewed = timezone.now()
            proposal.save()
        if form.instance.continuation == Review.LONG_ROUTE:
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
        if form.instance.continuation == Review.METC:
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

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Save the decision date"""
        form.instance.date_decision = timezone.now()
        return super(DecisionUpdateView, self).form_valid(form)
