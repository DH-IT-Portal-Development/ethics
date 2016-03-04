from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views import generic

from .forms import ReviewForm, DecisionForm
from .mixins import LoginRequiredMixin, UserAllowedMixin, AutoReviewMixin
from .models import Review, Decision


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


class ReviewDetailView(AutoReviewMixin, LoginRequiredMixin, UserAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review


class ReviewAssignView(AutoReviewMixin, LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """
    Allows a User of the SECRETARY group to assign reviewers.
    """
    model = Review
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('reviews:home')

    def form_valid(self, form):
        """Updates the review stage, creates Decisions and sends e-mail to reviewers."""
        form.instance.stage = Review.COMMISSION

        for user in form.cleaned_data['reviewers']:
            decision = Decision(review=form.instance, reviewer=user)
            decision.save()

            template = 'mail/assignment_shortroute.txt' if form.instance.short_route else 'mail/assignment_longroute.txt'

            subject = _('ETCL: nieuwe studie')
            params = {'reviewer': user.get_full_name(), 'secretary': 'Maartje de Klerk'}
            msg_plain = render_to_string(template, params)
            send_mail(subject, msg_plain, settings.EMAIL_FROM, [user.email])

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
