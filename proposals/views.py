# -*- coding: utf-8 -*-

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import ugettext_lazy as _

from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView

from .models import Proposal, Wmo, Study, Session, Task, Member, Meeting, Faq, Survey
from .forms import ProposalForm, ProposalCopyForm, WmoForm, StudyForm, \
    SessionStartForm, TaskStartForm, TaskForm, TaskEndForm, SessionEndForm, \
    UploadConsentForm, ProposalSubmitForm
from .copy import copy_proposal
from .utils import generate_ref_number


class LoginRequiredMixin(object):
    """Mixin for generic views to retun to login view if not logged in"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserAllowedMixin, self).get_object(queryset)

        applicants = []
        if isinstance(obj, Proposal):
            applicants = obj.applicants.all()
        elif isinstance(obj, Task):
            applicants = obj.session.proposal.applicants.all()
        else:
            applicants = obj.proposal.applicants.all()

        if self.request.user not in applicants:
            raise PermissionDenied
        return obj


class CreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    """Generic create view including success message and login required mixins"""
    pass


class UpdateView(SuccessMessageMixin, LoginRequiredMixin, UserAllowedMixin, generic.UpdateView):
    """Generic update view including success message and login required mixins"""
    pass


class DeleteView(LoginRequiredMixin, UserAllowedMixin, generic.DeleteView):
    """Generic delete view including login required mixin and alternative for success message"""
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).delete(request, *args, **kwargs)


class SurveysInline(InlineFormSet):
    model = Survey
    fields = ['name', 'minutes']
    can_delete = True
    extra = 1


# List views
class ArchiveView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'proposals'

    def get_queryset(self):
        """Return all the proposals"""
        return Proposal.objects.all().filter(status=9)


class IndexView(ArchiveView):
    def get_queryset(self):
        """Return all the submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status=9)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['submitted'] = True
        return context


class ConceptsView(ArchiveView):
    def get_queryset(self):
        """Return all the proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ConceptsView, self).get_context_data(**kwargs)
        context['concepts'] = True
        return context


class MembersView(generic.ListView):
    context_object_name = 'members'
    model = Member


class MeetingsView(generic.ListView):
    context_object_name = 'meetings'
    model = Meeting


class FaqsView(generic.ListView):
    context_object_name = 'faqs'
    model = Faq


# Proposal detail
class DetailView(LoginRequiredMixin, UserAllowedMixin, generic.DetailView):
    model = Proposal


# CRUD actions on Proposal
class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Conceptaanvraag %(title)s aangemaakt')

    def get_initial(self):
        """Set initial applicant to current user"""
        return {'applicants': [self.request.user]}

    def form_valid(self, form):
        """Set created_by to current user"""
        form.instance.created_by = self.request.user
        form.instance.reference_number = generate_ref_number(self.request.user)
        return super(ProposalCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Add 'create' parameter to form"""
        context = super(ProposalCreate, self).get_context_data(**kwargs)
        context['create'] = True
        return context

    def get_success_url(self):
        """Set the success_url based on the submit button pressed"""
        if 'save_continue' in self.request.POST:
            return self.object.continue_url()
        else:
            return reverse('proposals:my_concepts')


class ProposalCopy(CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _('Aanvraag gekopiëerd')
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
    # TODO: set date_submitted on form submit
    # TODO: send e-mail to supervisor on form submit


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


# CRUD actions on a Study
class StudyCreate(SuccessMessageMixin, LoginRequiredMixin, CreateWithInlinesView):
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]
    success_message = _('Algemene kenmerken opgeslagen')

    def forms_valid(self, form, inlines):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).forms_valid(form, inlines)

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class StudyUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateWithInlinesView):
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]
    success_message = _('Algemene kenmerken bewerkt')

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


# Actions on a Session
class ProposalSessionStart(ProposalUpdateView):
    form_class = SessionStartForm
    template_name = 'proposals/session_start.html'
    success_message = _('%(sessions_number)s sessies voor aanvraag %(title)s aangemaakt')

    def form_valid(self, form):
        # Create Sessions on save, if they don't exist
        # TODO: what if sessions_number is less than existing sessions?
        nr_sessions = form.cleaned_data['sessions_number']
        proposal = form.instance
        for n in xrange(nr_sessions):
            order = n + 1
            try:
                session = Session.objects.get(proposal=proposal, order=order)
            except ObjectDoesNotExist:
                session = Session(proposal=proposal, order=order)
                session.save()
        return super(ProposalSessionStart, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, title=self.object.title)


class ProposalSessionEnd(ProposalUpdateView):
    form_class = SessionEndForm
    template_name = 'proposals/session_end.html'
    success_message = ''


class SessionDelete(DeleteView):
    model = Session
    success_url = '/proposals/concepts/'
    success_message = _('Sessie verwijderd')


# CRUD actions on a Task
class TaskStart(UpdateView):
    model = Session
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_message = ''

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            # Go to the task creation for this session
            return reverse('proposals:task_create', args=(self.object.id,))
        else:
            return reverse('proposals:my_concepts')


class TaskEnd(UpdateView):
    model = Session
    form_class = TaskEndForm
    template_name = 'proposals/task_end.html'
    success_message = ''

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class TaskCreate(CreateView):
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
    model = Task
    success_url = '/proposals/concepts/'
    success_message = _('Taak verwijderd')


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'
