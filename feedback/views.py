from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views import generic

from .forms import FeedbackForm
from .models import Feedback


class LoginRequiredMixin(object):
    """Mixin for generic views to return to login view if not logged in"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class FeedbackCreate(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    success_message = _('Feedback verstuurd')

    def get_initial(self):
        """Sets URL to the referrer and submitter to current User"""
        initial = super(FeedbackCreate, self).get_initial()
        initial['url'] = self.request.META.get('HTTP_REFERER')
        return initial

    def form_valid(self, form):
        """Sets submitter to current user"""
        form.instance.submitter = self.request.user
        return super(FeedbackCreate, self).form_valid(form)

    def get_success_url(self):
        feedback = self.object
        return reverse('feedback:thanks', args=(feedback.pk,))


class FeedbackThanks(LoginRequiredMixin, generic.DetailView):
    model = Feedback
    template_name = 'feedback/feedback_thanks.html'


class FeedbackListing(LoginRequiredMixin, generic.ListView):
    model = Feedback
