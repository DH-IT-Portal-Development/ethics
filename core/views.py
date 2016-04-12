# -*- encoding: utf-8 -*-
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from proposals.models import Proposal
from observations.models import Observation
from interventions.models import Intervention
from tasks.models import Session, Task


################
# Views
################
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'


################
# AJAX callbacks
################
@csrf_exempt
def check_requires(request):
    """
    This call checks whether a certain value requires another input to be filled.
    """
    values = map(int, request.POST.getlist('value[]'))
    model = apps.get_model(request.POST.get('app'), request.POST.get('model'))
    required_values = model.objects.filter(**{request.POST.get('field'): True}).values_list('id', flat=True)
    result = bool(set(required_values).intersection(values))
    return JsonResponse({'result': result})


################
# Helpers
################
class AllowErrorsMixin(object):
    def form_invalid(self, form):
        """
        On back button, allow form to have errors.
        """
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(AllowErrorsMixin, self).form_invalid(form)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Allows access to a proposal based on the status of a Proposal
        and the position of the User. He can be:
        - in the 'SECRETARY' or 'COMMISSION' group
        - an applicant of this Proposal
        - a supervisor of this Proposal
        If the status of the Proposal is not in line with the status of the User,
        a PermissionDenied is raised.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Proposal):
            proposal = obj
        elif isinstance(obj, Observation) or isinstance(obj, Intervention) or isinstance(obj, Session):
            proposal = obj.study.proposal
        elif isinstance(obj, Task):
            proposal = obj.session.study.proposal
        else:
            proposal = obj.proposal

        applicants = proposal.applicants.all()
        if proposal.supervisor:
            supervisor = get_user_model().objects.filter(pk=proposal.supervisor.pk)
        else:
            supervisor = get_user_model().objects.none()
        commission = get_user_model().objects.filter(groups__name=settings.GROUP_SECRETARY)
        commission |= get_user_model().objects.filter(groups__name=settings.GROUP_COMMISSION)

        if proposal.status >= Proposal.SUBMITTED:
            if self.request.user not in commission:
                raise PermissionDenied
        elif proposal.status >= Proposal.SUBMITTED_TO_SUPERVISOR:
            if self.request.user not in supervisor:
                raise PermissionDenied
        else:
            if self.request.user not in applicants | supervisor:
                raise PermissionDenied

        return obj


class CreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    """Generic create view including success message and login required mixins"""
    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class UpdateView(LoginRequiredMixin, SuccessMessageMixin, UserAllowedMixin, generic.UpdateView):
    """Generic update view including success message, user allowed and login required mixins"""
    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class DeleteView(LoginRequiredMixin, UserAllowedMixin, generic.DeleteView):
    """Generic delete view including login required and user allowed mixin and alternative for success message"""
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).delete(request, *args, **kwargs)


def success_url(self):
    if 'save_continue' in self.request.POST:
        return self.get_next_url()
    if 'save_back' in self.request.POST:
        return self.get_back_url()
    else:
        return reverse('proposals:my_concepts')
