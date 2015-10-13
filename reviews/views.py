from django.views import generic

from .models import Review, Decision
from proposals.mixins import LoginRequiredMixin


class SupervisorView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'reviews'

    def get_queryset(self):
        """Return all the current open reviews for the current user"""
        return Review.objects.filter(date_end=None, stage=Review.SUPERVISOR, decision__reviewer=self.request.user)


class CommissionView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'reviews'

    def get_queryset(self):
        """Return all the current open reviews for the current user"""
        return Review.objects.filter(date_end=None, stage=Review.COMMISSION, decision__reviewer=self.request.user)


class DecisionView(LoginRequiredMixin, generic.UpdateView):
    model = Decision

    def get_object(self):
        return Decision.objects.filter(review=self.kwargs['pk'], reviewer=self.request.user).get()
