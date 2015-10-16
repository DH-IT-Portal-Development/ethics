from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Review, Decision
from .forms import DecisionForm
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


class DecisionUpdateView(LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    model = Decision
    form_class = DecisionForm

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Save the decision date"""
        form.instance.date_decision = timezone.now()
        return super(DecisionUpdateView, self).form_valid(form)
