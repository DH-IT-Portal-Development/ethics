from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Review, Decision
from .forms import ReviewForm, DecisionForm
from .mixins import LoginRequiredMixin, UserAllowedMixin


class DecisionListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Return all decisions of the current user"""
        return Decision.objects.filter(reviewer=self.request.user)


class SupervisorView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Return all the current open decisions for the current user"""
        return Decision.objects.filter(review__date_end=None, review__stage=Review.SUPERVISOR, reviewer=self.request.user)


class CommissionView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Return all the current open decisions for the current user"""
        return Decision.objects.all()  # filter(review__date_end=None, review__stage=Review.COMMISSION, reviewer=self.request.user)


class ReviewDetailView(LoginRequiredMixin, UserAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review


class ReviewAssignView(LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """
    Allows a superuser to assign reviewers.
    """
    model = Review
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Update the review status, create Decisions and (TODO) send e-mail to reviewers."""
        form.instance.stage = Review.COMMISSION
        for user in form.cleaned_data['reviewers']:
            decision = Decision(review=form.instance, reviewer=user)
            decision.save()
        return super(ReviewAssignView, self).form_valid(form)


class DecisionUpdateView(LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    model = Decision
    form_class = DecisionForm

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Save the decision date"""
        form.instance.date_decision = timezone.now()
        return super(DecisionUpdateView, self).form_valid(form)
