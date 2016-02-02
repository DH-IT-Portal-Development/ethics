from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .forms import ReviewForm, DecisionForm
from .mixins import LoginRequiredMixin, UserAllowedMixin
from .models import Review, Decision
from .utils import auto_review


class DecisionListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all Decisions of the current User"""
        return Decision.objects.filter(reviewer=self.request.user)


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


class ReviewDetailView(LoginRequiredMixin, UserAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review

    def get_context_data(self, **kwargs):
        """Adds the results of the machine-wise review to the context."""
        context = super(ReviewDetailView, self).get_context_data(**kwargs)
        go, reasons = auto_review(self.get_object().proposal)
        context['auto_review_go'] = go
        context['auto_review_reasons'] = reasons
        return context


class ReviewAssignView(LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """
    Allows a User of the SECRETARY group to assign reviewers.
    """
    model = Review
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Updates the review status, creates Decisions and sends e-mail to reviewers."""
        form.instance.stage = Review.COMMISSION
        emails = []
        for user in form.cleaned_data['reviewers']:
            decision = Decision(review=form.instance, reviewer=user)
            decision.save()
            emails.append(user.email)

        subject = 'ETCL: aanstellen commissieleden'
        message = 'Zie hier'
        send_mail(subject, message, settings.EMAIL_FROM, [emails])

        return super(ReviewAssignView, self).form_valid(form)


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
