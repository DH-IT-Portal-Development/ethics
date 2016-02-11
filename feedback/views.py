from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin

from .models import Feedback, Faq


class LoginRequiredMixin(object):
    """Mixin for generic views to return to login view if not logged in"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class FeedbackCreate(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = Feedback
    fields = ['comment']
    success_message = 'Feedback verstuurd'

    def form_valid(self, form):
        """Fill default fields"""
        form.instance.url = self.request.META.get('HTTP_REFERER')
        form.instance.submitter = self.request.user
        return super(FeedbackCreate, self).form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class FeedbackListing(LoginRequiredMixin, generic.ListView):
    model = Feedback


class FaqsView(generic.ListView):
    context_object_name = 'faqs'
    model = Faq
