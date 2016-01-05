# -*- encoding: utf-8 -*-

from django.apps import apps
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView
from easy_pdf.views import PDFTemplateResponseMixin

from .copy import copy_proposal
from .forms import ProposalForm, ProposalCopyForm, WmoForm, WmoCheckForm, StudyForm, \
    SessionStartForm, TaskStartForm, TaskForm, TaskEndForm, SessionEndForm, \
    UploadConsentForm, ProposalSubmitForm
from .mixins import LoginRequiredMixin, UserAllowedMixin
from .models import Proposal, Wmo, Study, Session, Task, Faq, Survey
from .utils import generate_ref_number, string_to_bool
from reviews.utils import start_review


class AllowErrorsMixin(object):
    def form_invalid(self, form):
        """On back button, allow form to have errors."""
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(AllowErrorsMixin, self).form_invalid(form)


def success_url(self):
    if 'save_continue' in self.request.POST:
        return self.get_next_url()
    if 'save_back' in self.request.POST:
        return self.get_back_url()
    else:
        return reverse('proposals:my_concepts')


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


# List views
class ProposalsView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'proposals'

    def get_queryset(self):
        """Returns all the proposals that have been decided upon"""
        return Proposal.objects.filter(status__gte=Proposal.DECISION_MADE)

    def get_context_data(self, **kwargs):
        context = super(ProposalsView, self).get_context_data(**kwargs)
        context['title'] = self.get_title()
        context['body'] = self.get_body()
        return context

    def get_title(self):
        return _('Publiek aanvraagarchief')

    def get_body(self):
        return _('Dit overzicht toont alle beoordeelde aanvragen.')


class MyConceptsView(ProposalsView):
    def get_queryset(self):
        """Returns all non-submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__lt=Proposal.SUBMITTED_TO_SUPERVISOR)

    def get_title(self):
        return _('Mijn conceptaanvragen')

    def get_body(self):
        return _('Dit overzicht toont al uw nog niet ingediende aanvragen.')


class MySubmittedView(ProposalsView):
    def get_queryset(self):
        """Returns all submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.SUBMITTED_TO_SUPERVISOR, status__lt=Proposal.DECISION_MADE)

    def get_title(self):
        return _('Mijn ingediende aanvragen')

    def get_body(self):
        return _('Dit overzicht toont al uw ingediende aanvragen.')


class MyCompletedView(ProposalsView):
    def get_queryset(self):
        """Returns all completed proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.DECISION_MADE)

    def get_title(self):
        return _('Mijn afgeronde aanvragen')

    def get_body(self):
        return _('Dit overzicht toont al uw beoordeelde aanvragen.')


class MyProposalsView(ProposalsView):
    def get_queryset(self):
        """Returns all proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user)

    def get_title(self):
        return _('Mijn aanvragen')

    def get_body(self):
        return _('Dit overzicht toont al uw aanvragen.')


class FaqsView(generic.ListView):
    context_object_name = 'faqs'
    model = Faq


##########################
# CRUD actions on Proposal
##########################
class DetailView(LoginRequiredMixin, generic.DetailView):
    # TODO: limit access to applicants, supervisor and commission
    model = Proposal


class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Conceptaanvraag %(title)s aangemaakt')

    def get_initial(self):
        """Sets initial applicant to current user"""
        return {'applicants': [self.request.user]}

    def form_valid(self, form):
        """Sets created_by to current user and generates a reference number"""
        form.instance.created_by = self.request.user
        form.instance.reference_number = generate_ref_number(self.request.user)
        return super(ProposalCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Adds 'create'/'no_back' to template context"""
        context = super(ProposalCreate, self).get_context_data(**kwargs)
        context['create'] = True
        context['no_back'] = True
        return context

    def get_next_url(self):
        proposal = self.object
        return reverse('proposals:wmo_create', args=(proposal.id,))


class ProposalUpdate(UpdateView):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Conceptaanvraag %(title)s bewerkt')

    def get_context_data(self, **kwargs):
        """Adds 'create'/'no_back' to template context"""
        context = super(ProposalUpdate, self).get_context_data(**kwargs)
        context['create'] = False
        context['no_back'] = True
        return context

    def get_next_url(self):
        proposal = self.object
        if hasattr(proposal, 'wmo'):
            return reverse('proposals:wmo_update', args=(proposal.id,))
        else:
            return reverse('proposals:wmo_create', args=(proposal.id,))


class ProposalDelete(DeleteView):
    model = Proposal
    success_message = _('Aanvraag verwijderd')

    def get_success_url(self):
        return reverse('proposals:my_concepts')


###########################
# Other actions on Proposal
###########################
class ProposalCopy(CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _('Aanvraag gekopieerd')
    template_name = 'proposals/proposal_copy.html'

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        form.instance = copy_proposal(self, form)
        return super(ProposalCopy, self).form_valid(form)


class ProposalUploadConsent(AllowErrorsMixin, UpdateView):
    model = Proposal
    form_class = UploadConsentForm
    template_name = 'proposals/proposal_consent.html'
    success_message = _('Informed consent geupload')

    def get_next_url(self):
        return reverse('proposals:submit', args=(self.object.id,))

    def get_back_url(self):
        return reverse('proposals:session_end', args=(self.object.id,))


class ProposalSubmit(UpdateView):
    model = Proposal
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_message = _('Aanvraag verzonden')

    def form_valid(self, form):
        """Start the review process on submission"""
        success_url = super(ProposalSubmit, self).form_valid(form)
        if not 'save_back' in self.request.POST:
            start_review(self.get_object())
        return success_url

    def get_next_url(self):
        return reverse('proposals:my_submitted')

    def get_back_url(self):
        return reverse('proposals:consent', args=(self.object.id,))


class ProposalAsPdf(LoginRequiredMixin, PDFTemplateResponseMixin, generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_pdf.html'


#####################
# CRUD actions on WMO
#####################
class WmoMixin(object):
    model = Wmo
    form_class = WmoForm

    def get_next_url(self):
        proposal = self.object.proposal
        if hasattr(proposal, 'study'):
            return reverse('proposals:study_update', args=(proposal.id,))
        else:
            return reverse('proposals:study_create', args=(proposal.id,))

    def get_back_url(self):
        return reverse('proposals:update', args=(self.object.proposal.id,))


class WmoCreate(WmoMixin, CreateView):
    success_message = _('WMO-gegevens opgeslagen')

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(WmoCreate, self).form_valid(form)


class WmoUpdate(WmoMixin, UpdateView):
    success_message = _('WMO-gegevens bewerkt')


######################
# Other actions on WMO
######################
class WmoCheck(generic.FormView):
    form_class = WmoCheckForm
    template_name = 'proposals/wmo_check.html'


#######################
# CRUD actions on Study
#######################
class SurveysInline(InlineFormSet):
    """Creates an InlineFormSet for Surveys"""
    model = Survey
    fields = ['name', 'minutes', 'survey_url']
    can_delete = True
    extra = 1


class StudyMixin(object):
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]

    def get_success_url(self):
        return success_url(self)

    def get_next_url(self):
        return reverse('proposals:session_start', args=(self.object.proposal.id,))

    def get_back_url(self):
        return reverse('proposals:wmo_update', args=(self.kwargs['pk'],))


# NOTE: below two views are non-standard, as they include inlines
# NOTE: no success message will be generated: https://github.com/AndrewIngram/django-extra-views/issues/59
class StudyCreate(StudyMixin, LoginRequiredMixin, CreateWithInlinesView):
    """Creates a Study from a StudyForm, with Surveys inlined."""

    def forms_valid(self, form, inlines):
        """Sets the Proposal on the Study before starting validation."""
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).forms_valid(form, inlines)

    def forms_invalid(self, form, inlines):
        """On back button, allow form to have errors."""
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(StudyCreate, self).forms_invalid(form, inlines)


class StudyUpdate(StudyMixin, LoginRequiredMixin, UserAllowedMixin, UpdateWithInlinesView):
    """Updates a Study from a StudyForm, with Surveys inlined."""


######################
# Actions on a Session
######################
class ProposalSessionStart(AllowErrorsMixin, UpdateView):
    """Initial creation of Sessions"""
    model = Proposal
    form_class = SessionStartForm
    template_name = 'proposals/session_start.html'
    success_message = _('%(sessions_number)s sessie(s) voor aanvraag %(title)s aangemaakt')

    def form_valid(self, form):
        """Creates or deletes Sessions on save"""
        nr_sessions = form.cleaned_data['sessions_number']
        proposal = form.instance
        current = proposal.session_set.count() or 0

        # Create sessions
        for n in xrange(current, nr_sessions):
            order = n + 1
            session = Session(proposal=proposal, order=order)
            session.save()

        # Delete sessions
        for n in xrange(nr_sessions, current):
            order = n + 1
            session = Session.objects.get(proposal=proposal, order=order)
            session.delete()

        # If the number of Sessions has changed, invalidate the Proposal fields
        if current != nr_sessions:
            proposal.sessions_duration = None
            proposal.sessions_stressful = None
            proposal.sessions_stressful_details = ''
            proposal.save()

        return super(ProposalSessionStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('proposals:task_start', args=(self.object.first_session().id,))

    def get_back_url(self):
        return reverse('proposals:study_update', args=(self.object.id,))

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


class ProposalSessionEnd(AllowErrorsMixin, UpdateView):
    """
    Completes the creation of Sessions
    """
    model = Proposal
    form_class = SessionEndForm
    template_name = 'proposals/session_end.html'
    success_message = _(u'Sessies toevoegen beëindigd')

    def get_initial(self):
        """If there is only one Session, transfer the data to Proposal level"""
        if self.object.sessions_number == 1:
            session = self.object.first_session()
            return {'sessions_stressful': session.tasks_stressful,
                    'sessions_stressful_details': session.tasks_stressful_details}
        else:
            return super(ProposalSessionEnd, self).get_initial()

    def get_next_url(self):
        return reverse('proposals:consent', args=(self.object.id,))

    def get_back_url(self):
        return reverse('proposals:task_end', args=(self.object.last_session().id,))


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


class TaskStart(AllowErrorsMixin, UpdateView):
    """Initially sets the total number of Tasks for a Session"""
    model = Session
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_message = _('%(tasks_number)s ta(a)k(en) aangemaakt')

    def form_valid(self, form):
        """Creates or deletes Tasks on save"""
        nr_tasks = form.cleaned_data['tasks_number']
        session = form.instance
        current = session.task_set.count() or 0

        # Create Tasks
        for n in xrange(current, nr_tasks):
            order = n + 1
            task = Task(session=session, order=order)
            task.save()

        # Delete Tasks
        for n in xrange(nr_tasks, current):
            order = n + 1
            task = Task.objects.get(session=session, order=order)
            task.delete()

        # If the number of Tasks has changed, invalidate the Session and Proposal fields
        if current != nr_tasks:
            session.tasks_duration = None
            session.tasks_stressful = None
            session.tasks_stressful_details = ''
            session.save()

            proposal = session.proposal
            proposal.sessions_duration = None
            proposal.sessions_stressful = None
            proposal.sessions_stressful_details = ''
            proposal.save()

        return super(TaskStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('proposals:task_update', args=(self.object.first_task().id,))

    def get_back_url(self):
        try:
            # Try to return to task_end of the previous Session
            prev_session = Session.objects.get(proposal=self.object.proposal, order=self.object.order - 1)
            return reverse('proposals:task_end', args=(prev_session.id,))
        except Session.DoesNotExist:
            # If this is the first Session, return to session_start
            return reverse('proposals:session_start', args=(self.object.proposal.id,))


def add_task(request, pk):
    """Updates the tasks_number on a Session"""
    # TODO: fix this or delete functionality.
    session = get_object_or_404(Session, pk=pk)
    session.tasks_number += 1
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_create', args=(session.id,)))


class TaskEnd(AllowErrorsMixin, UpdateView):
    """Completes a Session"""
    model = Session
    form_class = TaskEndForm
    template_name = 'proposals/task_end.html'
    success_message = _(u'Taken toevoegen beëindigd')

    def get_next_url(self):
        try:
            # Try to continue to next Session
            next_session = Session.objects.get(proposal=self.object.proposal, order=self.object.order + 1)
            return reverse('proposals:task_start', args=(next_session.id,))
        except Session.DoesNotExist:
            # If this is the last Session, continue to session_end
            return reverse('proposals:session_end', args=(self.object.proposal.id,))

    def get_back_url(self):
        return reverse('proposals:task_update', args=(self.object.last_task().id,))


######################
# CRUD actions on Task
######################
class TaskUpdate(AllowErrorsMixin, UpdateView):
    """Updates a Task"""
    model = Task
    form_class = TaskForm
    success_message = _('Taak bewerkt')

    def get_next_url(self):
        try:
            # Try to continue to next Task
            next_task = Task.objects.get(session=self.object.session, order=self.object.order + 1)
            return reverse('proposals:task_update', args=(next_task.id,))
        except Task.DoesNotExist:
            # If this is the last Task, continue to task_end
            return reverse('proposals:task_end', args=(self.object.session.id,))

    def get_back_url(self):
        try:
            # Try to return to previous Task
            prev_task = Task.objects.get(session=self.object.session, order=self.object.order - 1)
            return reverse('proposals:task_update', args=(prev_task.id,))
        except Task.DoesNotExist:
            # If this is the first Task, return to task_start
            return reverse('proposals:task_start', args=(self.object.session.id,))


class TaskDelete(DeleteView):
    """Deletes a Task"""
    model = Task
    success_message = _('Taak verwijderd')

    def get_success_url(self):
        # TODO: fix task order just like sessions above
        return reverse('proposals:detail', args=(self.object.session.proposal.id,))


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


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


@csrf_exempt
def check_wmo(request):
    """
    This call checks which WMO message should be generated.
    """
    is_metc = string_to_bool(request.POST.get('metc'))
    is_medical = string_to_bool(request.POST.get('medical'))
    is_behavioristic = string_to_bool(request.POST.get('behavioristic'))

    # Default message: OK.
    message = _('Uw aanvraag hoeft niet te worden beoordeeld door de METC.')
    message_class = 'info'

    if is_metc is None or (not is_metc and is_medical is None):
        message = _('Neem contact op met Maartje de Klerk om de twijfels weg te nemen.')
        message_class = 'warning'
    elif is_metc or (is_medical and is_behavioristic):
        message = _('Uw aanvraag zal moeten worden beoordeeld door de METC.')
        message_class = 'warning'

    return JsonResponse({'message': message, 'message_class': message_class})
