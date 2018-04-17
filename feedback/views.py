from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views import generic

from braces.views import LoginRequiredMixin

from .forms import FeedbackForm
from .models import Feedback


class FeedbackCreate(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    success_message = _('Feedback verstuurd')

    def get_initial(self):
        """Sets URL to the referrer and submitter to current User"""
        initial = super(FeedbackCreate, self).get_initial()
        initial['url'] = self.request.META.get('HTTP_REFERER')
        return initial

    def form_valid(self, form):
        """Sets submitter to current User"""
        form.instance.submitter = self.request.user
        return super(FeedbackCreate, self).form_valid(form)

    def get_success_url(self):
        """Redirect to thank-you page"""
        return reverse('feedback:thanks', args=(self.object.pk,))


class FeedbackThanks(LoginRequiredMixin, generic.DetailView):
    model = Feedback
    template_name = 'feedback/feedback_thanks.html'


class FeedbackListing(LoginRequiredMixin, generic.ListView):
    model = Feedback
