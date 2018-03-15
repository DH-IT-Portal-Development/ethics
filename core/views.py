# -*- encoding: utf-8 -*-
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.models import User

from braces.views import LoginRequiredMixin

from proposals.models import Proposal
from observations.models import Observation
from interventions.models import Intervention
from tasks.models import Session, Task

import ldap

# We set up a custom LDAP connection here, separate from the Django auth one
try:
    # This will trigger an exception if LDAP is not configured
    from etcl.ldap_settings import *

    # If it is configured, we open a connection and bind our credentials to it.
    ldap_connection = ldap.initialize(AUTH_LDAP_SERVER_URI)
    ldap_connection.bind(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)

    # If all went well, we mark our connection as available
    ldap_available = True
except (ImportError, ldap.LDAPError):
    # If there was a problem importing or connecting to the LDAP, we mark our connection as not available
    ldap_available = False


################
# Views
################
class HomeView(generic.TemplateView):
    template_name = 'core/index.html'


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


def user_search(query, page):
    """
    This function searches through users for a given query. Page 1 will return registered users, or if there are none,
    LDAP users. Page 2 will return LDAP users.

    The double behaviour of page 1 has to be this weird because of the way Select2 handles empty pages.

    If a page returns LDAP users, or there is no LDAP connection available, we will mark the page as the last page.
    """
    # We begin with an empty list
    users = []

    # If we have a wildcard or an empty query, we just show all users
    if query == u'*' or query == u'':
        users = format_user_info(User.objects.all())
    elif page == u'1':
        # Otherwise we search through the users with a given query
        data = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        users = format_user_info(data)

    # We need results from the LDAP if either, this is page 2, or page 1 has no results for now
    # We put this in a variable because we're going to reuse this later on
    ldap_results_needed = (page == u'2' or len(users) < 3)

    # If we can use the LDAP and we need LDAP results
    if ldap_available and ldap_results_needed:
        # Start the LDAP search
        ldap_query = escape_ldap_input(query)
        msgid = ldap_connection.search(
            'ou=People,dc=uu,dc=nl',
            ldap.SCOPE_SUBTREE,
            filterstr='(|(humAchternaam=*{}*)(uid=*{}*)(givenName=*{}*)(displayName=*{}*))'.format(
                ldap_query,
                ldap_query,
                ldap_query,
                ldap_query
            )
        )
        # Get results and loop over them
        for _, data in ldap_connection.result(msgid)[1]:
            # Add them to the users, with a ldap_ prefix in the ID so we can distinguish this when processing the form
            users.append({
                'id': 'ldap_' + data.get('uid')[0],
                'text': '{}: {}'.format(data.get('uid')[0], data.get('displayName')[0])
            })

    # Return a formatted dict with the results
    return {
        'results': users,
        # Paging-more should be true if there are no LDAP results included in this page, the LDAP is available and
        # the query is not a wildcard
        'pagination': {'more': not ldap_results_needed and ldap_available and query != '*'}
    }


def escape_ldap_input(string):
    """
    This function escapes the user input such that all values are seen as text, not filter instructions.

    TL;DR: prevents LDAP injection

    :param string string: The to be escaped string
    :return string: The escaped string
    """
    escape_vals = {
        '\\': r'\5c',
        r'(': r'\28',
        r'|': r'\7c',
        r'<': r'\3c',
        r'/': r'\2f',
        r')': r'\29',
        r'=': r'\3d',
        r'~': r'\7e',
        r'&': r'\26',
        r'>': r'\3e',
        r'*': r'\2a'
    }

    for x, y in escape_vals.items():
        string = string.replace(x, y)

    return string.strip(" ")


def format_user_info(lst):
    """This will format a user object into a displayable format"""
    return [{'id': x.pk, 'text': u'{}: {}'.format(x.username, x.get_full_name())} for x in lst]


class UserSearchView(LoginRequiredMixin, generic.View):

    def render_to_response(self, context, *args, **kwargs):
        return JsonResponse(context, *args, **kwargs)

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q')
        page = self.request.GET.get('page')
        context = user_search(query, page)

        return self.render_to_response(context)


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
