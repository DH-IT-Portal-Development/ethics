# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView

from .copy import copy_proposal
from .forms import ProposalForm, ProposalCopyForm, WmoForm, WmoCheckForm, StudyForm, \
    SessionStartForm, TaskStartForm, TaskForm, TaskEndForm, SessionEndForm, \
    UploadConsentForm, ProposalSubmitForm
from .mixins import LoginRequiredMixin, UserAllowedMixin
from .models import Proposal, Wmo, Study, Session, Task, Faq, Survey, Relation, \
    Trait, Setting, Compensation, Recruitment
from .utils import generate_ref_number
from reviews.utils import start_review


class CreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    """Generic create view including success message and login required mixins"""
    pass


class UpdateView(SuccessMessageMixin, LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """Generic update view including success message, user allowed and login required mixins"""
    pass


class DeleteView(LoginRequiredMixin, UserAllowedMixin, generic.DeleteView):
    """Generic delete view including login required and user allowed mixin and alternative for success message"""
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).delete(request, *args, **kwargs)


class SurveysInline(InlineFormSet):
    model = Survey
    fields = ['name', 'minutes', 'survey_url', 'survey_file']
    can_delete = True
    extra = 1


# List views
class ArchiveView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'proposals'

    def get_queryset(self):
        """Return all the proposals"""
        return Proposal.objects.all().filter(status__gte=Proposal.DECISION_MADE)


class IndexView(ArchiveView):
    def get_queryset(self):
        """Return all the submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.SUBMITTED_TO_SUPERVISOR)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['submitted'] = True
        return context


class ConceptsView(ArchiveView):
    def get_queryset(self):
        """Return all the non-submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__lt=Proposal.SUBMITTED_TO_SUPERVISOR)

    def get_context_data(self, **kwargs):
        context = super(ConceptsView, self).get_context_data(**kwargs)
        context['concepts'] = True
        return context


class FaqsView(generic.ListView):
    context_object_name = 'faqs'
    model = Faq


# Proposal detail
class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Proposal


# CRUD actions on Proposal
class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Conceptaanvraag %(title)s aangemaakt')

    def get_initial(self):
        """Sets initial applicant to current user"""
        return {'applicants': [self.request.user]}

    def form_valid(self, form):
        """Sets created_by to current user and generate a reference number"""
        form.instance.created_by = self.request.user
        form.instance.reference_number = generate_ref_number(self.request.user)
        return super(ProposalCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Adds 'create' parameter to form"""
        context = super(ProposalCreate, self).get_context_data(**kwargs)
        context['create'] = True
        return context

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        if 'save_continue' in self.request.POST:
            return self.object.continue_url()
        else:
            return reverse('proposals:my_concepts')


class ProposalCopy(CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _('Aanvraag gekopieerd')
    success_url = '/proposals/concepts/'
    template_name = 'proposals/proposal_copy.html'

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        form.instance = copy_proposal(self, form)
        return super(ProposalCopy, self).form_valid(form)


class ProposalUpdateView(UpdateView):
    model = Proposal

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.continue_url()
        else:
            return reverse('proposals:my_concepts')


class ProposalUpdate(ProposalUpdateView):
    form_class = ProposalForm
    success_message = _('Conceptaanvraag %(title)s bewerkt')


class ProposalUploadConsent(ProposalUpdateView):
    form_class = UploadConsentForm
    template_name = 'proposals/proposal_consent.html'
    success_message = _('Informed consent geupload')


class ProposalSubmit(ProposalUpdateView):
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_message = _('Aanvraag verzonden')

    def form_valid(self, form):
        """Start the review process on submission"""
        success_url = super(ProposalSubmit, self).form_valid(form)
        start_review(self.get_object())
        return success_url

    def get_success_url(self):
        return reverse('proposals:my_archive')


class ProposalDelete(DeleteView):
    model = Proposal
    success_url = '/proposals/concepts/'
    success_message = _('Aanvraag verwijderd')


# CRUD actions on Wmo
class WmoCreate(CreateView):
    model = Wmo
    form_class = WmoForm
    success_message = _('WMO-gegevens opgeslagen')

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(WmoCreate, self).form_valid(form)

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class WmoUpdate(UpdateView):
    model = Wmo
    form_class = WmoForm
    success_message = _('WMO-gegevens bewerkt')

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class WmoCheck(generic.FormView):
    form_class = WmoCheckForm
    template_name = 'proposals/wmo_check.html'


# CRUD actions on a Study
# TODO: no success message: https://github.com/AndrewIngram/django-extra-views/issues/59
class StudyCreate(LoginRequiredMixin, CreateWithInlinesView):
    """Creates a Study from a StudyForm, with Surveys inlined."""
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]

    def forms_valid(self, form, inlines):
        """Sets the Proposal on the Study before starting validation."""
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).forms_valid(form, inlines)

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class StudyUpdate(LoginRequiredMixin, UserAllowedMixin, UpdateWithInlinesView):
    """Updates a Study from a StudyForm, with Surveys inlined."""
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


# Actions on a Session
class ProposalSessionStart(ProposalUpdateView):
    """Initial creation of Sessions"""
    form_class = SessionStartForm
    template_name = 'proposals/session_start.html'
    success_message = _('%(sessions_number)s sessies voor aanvraag %(title)s aangemaakt')

    def form_valid(self, form):
        # Create Sessions on save. TODO: don't allow coming here later...
        nr_sessions = form.cleaned_data['sessions_number']
        proposal = form.instance
        for n in xrange(nr_sessions):
            order = n + 1
            session = Session(proposal=proposal, order=order)
            session.save()
        return super(ProposalSessionStart, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, title=self.object.title)


def add_session(request, pk):
    """Adds a Session to the given Proposal"""
    proposal = get_object_or_404(Proposal, pk=pk)
    new_session_number = proposal.sessions_number + 1

    proposal.sessions_number = new_session_number
    proposal.save()

    session = Session(proposal=proposal, order=new_session_number)
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_start', args=(session.id,)))


class ProposalSessionEnd(ProposalUpdateView):
    form_class = SessionEndForm
    template_name = 'proposals/session_end.html'
    success_message = ''


class SessionDelete(DeleteView):
    model = Session
    success_message = _('Sessie verwijderd')

    def get_success_url(self):
        return reverse('proposals:detail', args=(self.object.proposal.id,))

    def delete(self, request, *args, **kwargs):
        """
        Deletes the Session and updates the Proposal and other Sessions.
        Completely overrides the default delete function (as that calls delete too late for us).
        TODO: maybe save the HttpResponseRedirect and then perform the other actions?
        """
        self.object = self.get_object()
        order = self.object.order
        proposal = self.object.proposal
        success_url = self.get_success_url()
        self.object.delete()

        # If the session number is lower than the total number of sessions (e.g. 3 of 4),
        # set the other session numbers one lower
        for s in Session.objects.filter(proposal=proposal, order__gt=order):
            s.order -= 1
            s.save()

        # Set the number of sessions on Proposal
        proposal.sessions_number -= 1
        proposal.save()

        return HttpResponseRedirect(success_url)


class TaskStart(UpdateView):
    """Initially sets the total number of Tasks for a Session"""
    model = Session
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_message = ''

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


def add_task(request, pk):
    """Updates the tasks_number on a Session"""
    session = get_object_or_404(Session, pk=pk)
    session.tasks_number += 1
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_create', args=(session.id,)))


class TaskEnd(UpdateView):
    """Completes the Session"""
    model = Session
    form_class = TaskEndForm
    template_name = 'proposals/task_end.html'
    success_message = ''

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


# CRUD actions on a Task
class TaskCreate(CreateView):
    """Creates a Task"""
    model = Task
    form_class = TaskForm
    success_message = _('Taak opgeslagen')

    def get_context_data(self, **kwargs):
        context = super(TaskCreate, self).get_context_data(**kwargs)
        session = Session.objects.get(pk=self.kwargs['pk'])
        task_count = session.task_set.count() + 1
        context['session'] = session
        context['save_add_button'] = task_count < session.tasks_number
        context['task_count'] = task_count
        return context

    def form_valid(self, form):
        form.instance.session = Session.objects.get(pk=self.kwargs['pk'])
        return super(TaskCreate, self).form_valid(form)

    def get_success_url(self):
        if 'save_add' in self.request.POST:
            return reverse('proposals:task_create', args=(self.kwargs['pk'],))
        elif 'save_continue' in self.request.POST:
            return self.object.session.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class TaskUpdate(UpdateView):
    """Updates a Task"""
    model = Task
    form_class = TaskForm
    success_message = _('Taak bewerkt')

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        session = Task.objects.get(pk=self.kwargs['pk']).session
        task_count = session.task_set.count() + 1
        context['session'] = session
        context['save_add_button'] = task_count < session.tasks_number
        context['task_count'] = task_count - 1
        return context

    def get_success_url(self):
        task = Task.objects.get(pk=self.kwargs['pk'])
        if 'save_add' in self.request.POST:
            return reverse('proposals:task_create', args=(task.session.id,))
        elif 'save_continue' in self.request.POST:
            return self.object.session.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class TaskDelete(DeleteView):
    """Deletes a Task"""
    model = Task
    success_message = _('Taak verwijderd')

    def get_success_url(self):
        return reverse('proposals:detail', args=(self.object.session.proposal.id,))


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        #context['reviews_supervisor'] = Review.objects.filter(date_end=None, stage=Review.SUPERVISOR, decision__reviewer=self.request.user)
        #context['reviews_commission'] = Review.objects.filter(date_end=None, stage=Review.COMMISSION, decision__reviewer=self.request.user)
        return context


@csrf_exempt
def requires_supervisor(request):
    value = map(int, request.POST.getlist('value[]'))
    needs_supervisor = Relation.objects.filter(needs_supervisor=True).values_list('id', flat=True)
    result = bool(set(needs_supervisor).intersection(value))
    return JsonResponse({'result': result})


@csrf_exempt
def requires_traits_details(request):
    value = map(int, request.POST.getlist('value[]'))
    requires_traits_details = Trait.objects.filter(needs_details=True).values_list('id', flat=True)
    result = bool(set(requires_traits_details).intersection(value))
    return JsonResponse({'result': result})


@csrf_exempt
def requires_settings_details(request):
    value = map(int, request.POST.getlist('value[]'))
    requires_settings_details = Setting.objects.filter(needs_details=True).values_list('id', flat=True)
    result = bool(set(requires_settings_details).intersection(value))
    return JsonResponse({'result': result})


@csrf_exempt
def requires_compensation_details(request):
    value = map(int, request.POST.getlist('value[]'))
    requires_compensation_details = Compensation.objects.filter(needs_details=True).values_list('id', flat=True)
    result = bool(set(requires_compensation_details).intersection(value))
    return JsonResponse({'result': result})


@csrf_exempt
def requires_recruitment_details(request):
    value = map(int, request.POST.getlist('value[]'))
    requires_recruitment_details = Recruitment.objects.filter(needs_details=True).values_list('id', flat=True)
    result = bool(set(requires_recruitment_details).intersection(value))
    return JsonResponse({'result': result})
