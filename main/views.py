# -*- encoding: utf-8 -*-
import ldap
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin

from interventions.models import Intervention
from observations.models import Observation
from proposals.models import Proposal
from reviews.models import Review
from tasks.models import Session, Task

try:
    # This will trigger an exception if LDAP is not configured
    from fetc.ldap_settings import *
    LDAP_CONFIGURED = True
except (ImportError):
    LDAP_CONFIGURED = False


################
# Views
################
class HomeView(generic.TemplateView):
    template_name = 'main/index.html'


class UserDetailView(GroupRequiredMixin, generic.DetailView):
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_LINGUISTICS_CHAMBER,
        settings.GROUP_GENERAL_CHAMBER,
    ]
    model = get_user_model()
    context_object_name = 'user_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['reviews'] = self.get_user_reviews()

        return context

    def get_user_reviews(self):
        """Returns all Committee Reviews of this user"""
        reviews = {}
        objects = Review.objects.filter(
            stage__gte=Review.ASSIGNMENT,
            proposal__status__gte=Proposal.SUBMITTED,
            proposal__created_by=self.get_object()
        )

        for obj in objects:
            proposal = obj.proposal
            if proposal not in reviews:
                reviews[proposal.pk] = obj
            else:
                if reviews[proposal.pk].pk < obj.pk:
                    reviews[proposal.pk] = obj

        return [value for key, value in reviews.items()]


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
    required_values = model.objects.filter(**{
        request.POST.get('field'): True
    }).values_list('id', flat=True)
    result = bool(set(required_values).intersection(values))
    return JsonResponse({
                            'result': result
                        })

def establish_ldap_connection():
    # We set up a custom LDAP connection here, separate from the Django auth one
    if not LDAP_CONFIGURED:
        return None
    try:
        # If LDAP is configured, we open a connection and bind our credentials to it.
        ldap_connection = ldap.initialize(AUTH_LDAP_SERVER_URI)
        ldap_connection.bind(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)
        return ldap_connection
    except ldap.LDAPError:
        # Raised if there was a problem connecting to LDAP
        return None

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
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(
                last_name__icontains=query))
        users = format_user_info(data)

    # We need results from the LDAP if either, this is page 2, or page 1 has no results for now
    # We put this in a variable because we're going to reuse this later on
    ldap_results_needed = (page == u'2' or len(users) == 0)

    # Attempt to establish LDAP connection
    ldap_connection = establish_ldap_connection()

    # If we can use the LDAP and we need LDAP results
    if ldap_connection and ldap_results_needed:
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
                'id':   'ldap_' + data.get('uid')[0].decode("utf-8"),
                'text': '{}: {}'.format(data.get('uid')[0].decode("utf-8"),
                                        data.get('displayName')[0].decode(
                                            "utf-8"))
            })

    # Paging-more should be true if there are no LDAP results included in this page, the LDAP is available and
    # the query is not a wildcard
    paging_more = not ldap_results_needed and ldap_connection and query != '*'
    
    # Unbind the ldap connection after we are done with it
    if ldap_connection:
        ldap_connection.unbind()
    
    # Return a formatted dict with the results
    return {
        'results':    users,
        'pagination': {
            'more': paging_more
        }
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
    return [{
                'id':   x.pk,
                'text': u'{}: {}'.format(x.username, x.get_full_name())
            } for x in lst]


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
class AllowErrorsOnBackbuttonMixin(object):
    def form_invalid(self, form):
        """
        On back button, allow form to have errors.
        """
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(AllowErrorsOnBackbuttonMixin, self).form_invalid(form)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Allows access to a proposal based on the status of a Proposal
        and the position of the User. He can be:
        - in the 'SECRETARY', 'GENERAL_CHAMBER' or 'LINGUISTICS_CHAMBER' group
        - an applicant of this Proposal
        - a supervisor of this Proposal
        If the status of the Proposal is not in line with the status of the User,
        a PermissionDenied is raised.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Proposal):
            proposal = obj
        elif isinstance(obj, Observation) or isinstance(obj,
                                                        Intervention) or isinstance(
                obj, Session):
            proposal = obj.study.proposal
        elif isinstance(obj, Task):
            proposal = obj.session.study.proposal
        else:
            proposal = obj.proposal

        applicants = proposal.applicants.all()
        if proposal.supervisor:
            supervisor = get_user_model().objects.filter(
                pk=proposal.supervisor.pk)
        else:
            supervisor = get_user_model().objects.none()
        commission = get_user_model().objects.filter(groups__name=settings.GROUP_SECRETARY)
        if proposal.reviewing_committee.name == settings.GROUP_LINGUISTICS_CHAMBER:
            commission |= get_user_model().objects.filter(
                groups__name=settings.GROUP_LINGUISTICS_CHAMBER)
        if proposal.reviewing_committee.name == settings.GROUP_GENERAL_CHAMBER:
            commission |= get_user_model().objects.filter(
                groups__name=settings.GROUP_GENERAL_CHAMBER)

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


class FormSetUserAllowedMixin(UserAllowedMixin):

    def check_allowed(self):
        """
        Allows access to a proposal based on the status of a Proposal
        and the position of the User. He can be:
        - in the 'SECRETARY', 'LINGUISITICS_CHAMBER' or 'GENERAL_CHAMBER' group
        - an applicant of this Proposal
        - a supervisor of this Proposal
        If the status of the Proposal is not in line with the status of the User,
        a PermissionDenied is raised.
        """

        for obj in self.objects:

            if isinstance(obj, Proposal):
                proposal = obj
            elif isinstance(obj, Observation) or isinstance(obj,
                                                            Intervention) or isinstance(
                    obj, Session):
                proposal = obj.study.proposal
            elif isinstance(obj, Task):
                proposal = obj.session.study.proposal
            else:
                proposal = obj.proposal

            applicants = proposal.applicants.all()
            if proposal.supervisor:
                supervisor = get_user_model().objects.filter(
                    pk=proposal.supervisor.pk)
            else:
                supervisor = get_user_model().objects.none()
            commission = get_user_model().objects.filter(groups__name=settings.GROUP_SECRETARY)

            if proposal.reviewing_committee.name == settings.GROUP_LINGUISTICS_CHAMBER:
                commission |= get_user_model().objects.filter(
                    groups__name=settings.GROUP_LINGUISTICS_CHAMBER
                )

            if proposal.reviewing_committee.name == settings.GROUP_GENERAL_CHAMBER:
                commission |= get_user_model().objects.filter(
                    groups__name=settings.GROUP_GENERAL_CHAMBER
                )

            if proposal.status >= Proposal.SUBMITTED:
                if self.request.user not in commission:
                    raise PermissionDenied
            elif proposal.status >= Proposal.SUBMITTED_TO_SUPERVISOR:
                if self.request.user not in supervisor:
                    raise PermissionDenied
            else:
                if self.request.user not in applicants | supervisor:
                    raise PermissionDenied


class CreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    """Generic create view including success message and login required
    mixins"""

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class UpdateView(LoginRequiredMixin, SuccessMessageMixin, UserAllowedMixin,
                 generic.UpdateView):
    """Generic update view including success message, user allowed and login
    required mixins"""

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class FormSetUpdateView(FormSetUserAllowedMixin, LoginRequiredMixin,
                        SuccessMessageMixin, generic.View):
    """ Generic update view that uses a formset. This allows you to edit
    multiple forms of the same type on the same page.
    """
    form = None
    _formset = None
    queryset = None
    extra = 0

    def get(self, request, *args, **kwargs):
        self._on_request()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self._on_request()

        formset = self._formset(request.POST, request.FILES,
                                queryset=self.objects)
        self.pre_validation(formset)
        if formset.is_valid():
            self.save_form(formset)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name,
                          self.get_context_data(formset=formset))

    def pre_validation(self, formset):
        """This method can be overridden to manipulate the formset before
        validation"""
        pass

    def save_form(self, formset):
        formset.save()

    def _on_request(self):
        self._formset = modelformset_factory(self.form._meta.model,
                                             form=self.form, extra=self.extra)
        self.objects = self.get_queryset()
        self.check_allowed()

    def get_queryset(self):
        if self.queryset is None:
            raise ImproperlyConfigured(
                "Either override get_queryset, or provide a queryset class "
                "variable")

        return self.queryset

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self

        kwargs['objects'] = self.objects

        if 'formset' not in kwargs:
            kwargs['formset'] = self._formset(queryset=self.objects)

        return kwargs


class DeleteView(LoginRequiredMixin, UserAllowedMixin, generic.DeleteView):
    """Generic delete view including login required and user allowed mixin and
    alternative for success message"""

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
