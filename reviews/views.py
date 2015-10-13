from django.views import generic

from .models import Review
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
