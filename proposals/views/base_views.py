# -*- encoding: utf-8 -*-

from django.apps import apps
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from ..mixins import LoginRequiredMixin, UserAllowedMixin
from ..models import Faq

SESSION_PROGRESS_START = 20
SESSION_PROGRESS_TOTAL = 60
SESSION_PROGRESS_EPSILON = 5


class CreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    """Generic create view including success message and login required mixins"""
    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class UpdateView(SuccessMessageMixin, LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """Generic update view including success message, user allowed and login required mixins"""
    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class DeleteView(LoginRequiredMixin, UserAllowedMixin, generic.DeleteView):
    """Generic delete view including login required and user allowed mixin and alternative for success message"""
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).delete(request, *args, **kwargs)


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


# TODO: move to feedback app
class FaqsView(generic.ListView):
    context_object_name = 'faqs'
    model = Faq


################
# AJAX callbacks
################
@csrf_exempt
def check_requires(request):
    """
    This call checks whether a certain value requires another input to be filled.
    """
    values = map(int, request.POST.getlist('value[]'))
    model = apps.get_model('proposals', request.POST.get('model'))
    required_values = model.objects.filter(**{request.POST.get('field'): True}).values_list('id', flat=True)
    result = bool(set(required_values).intersection(values))
    return JsonResponse({'result': result})


#########
# Helpers
#########

def success_url(self):
    if 'save_continue' in self.request.POST:
        return self.get_next_url()
    if 'save_back' in self.request.POST:
        return self.get_back_url()
    else:
        return reverse('proposals:my_concepts')


def get_session_progress(session, is_end=False):
    progress = SESSION_PROGRESS_TOTAL / session.proposal.sessions_number
    if not is_end:
        progress *= (session.order - 1)
    else:
        progress *= session.order
    return SESSION_PROGRESS_START + progress


def get_task_progress(task):
    session = task.session
    session_progress = get_session_progress(session)
    task_progress = task.order / float(session.tasks_number)
    return int(session_progress + (SESSION_PROGRESS_TOTAL / session.proposal.sessions_number) * task_progress - SESSION_PROGRESS_EPSILON)
