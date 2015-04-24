from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import generic
from django.core.urlresolvers import reverse

from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView

from .models import Proposal, Wmo, Study, Task, Member, Meeting, Faq, Survey
from .forms import ProposalForm, ProposalCopyForm, WmoForm, StudyForm, \
    TaskStartForm, TaskForm, TaskEndForm, UploadConsentForm, ProposalSubmitForm


class LoginRequiredMixin(object):
    """Mixin for generic views to retun to login view if not logged in"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    """Generic create view including success message and login required mixins"""
    pass


class UpdateView(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    """Generic update view including success message and login required mixins"""
    pass


class DeleteView(LoginRequiredMixin, generic.DeleteView):
    """Generic delete view including login required mixin and alternative for success message"""
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).delete(request, *args, **kwargs)


class SurveysInline(InlineFormSet):
    model = Survey


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
class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Proposal


# CRUD actions on Proposal
class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm
    success_message = 'Conceptaanvraag %(title)s aangemaakt'

    def get_initial(self):
        """Set initial applicant to current user"""
        return {'applicants': [self.request.user]}

    def form_valid(self, form):
        """Set created_by to current user"""
        form.instance.created_by = self.request.user
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
    success_message = 'Aanvraag gekopieerd'
    success_url = '/proposals/concepts/'
    template_name = 'proposals/proposal_copy.html'

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        parent = form.cleaned_data['parent']
        form.instance = parent
        form.instance.pk = None
        form.instance.title = 'Kopie van %s' % form.instance.title
        form.instance.relation = parent.relation
        form.instance.created_by = self.request.user
        #form.instance.applicants = parent.applicants TODO: why doesn't this work? maybe deepcopy?!
        form.instance.parent = parent
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
    success_message = 'Conceptaanvraag %(title)s bewerkt'


class ProposalTaskStart(ProposalUpdateView):
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_message = ''


class ProposalTaskEnd(ProposalUpdateView):
    form_class = TaskEndForm
    template_name = 'proposals/task_end.html'
    success_message = ''


class ProposalUploadConsent(ProposalUpdateView):
    form_class = UploadConsentForm
    template_name = 'proposals/proposal_consent.html'
    success_message = 'Informed consent geupload'


class ProposalSubmit(ProposalUpdateView):
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_message = 'Aanvraag verzonden'
    # TODO: set date_submitted on form submit
    # TODO: send e-mail to supervisor on form submit


class ProposalDelete(DeleteView):
    model = Proposal
    success_url = '/proposals/concepts/'
    success_message = 'Aanvraag verwijderd'


# CRUD actions on Wmo
class WmoCreate(CreateView):
    model = Wmo
    form_class = WmoForm
    success_message = 'WMO-gegevens opgeslagen'

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
    success_message = 'WMO-gegevens bewerkt'

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


# CRUD actions on a Study
class StudyCreate(CreateView):
    model = Study
    form_class = StudyForm
    success_message = 'Algemene kenmerken opgeslagen'

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).form_valid(form)

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class StudyUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateWithInlinesView):
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]
    success_message = 'Algemene kenmerken bewerkt'

    def get_success_url(self):
        if 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


# CRUD actions on a Task
class TaskCreate(CreateView):
    model = Task
    form_class = TaskForm
    success_message = 'Taak opgeslagen'

    def get_context_data(self, **kwargs):
        context = super(TaskCreate, self).get_context_data(**kwargs)
        proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        task_count = proposal.task_set.count() + 1
        context['proposal'] = proposal
        context['save_add_button'] = task_count < proposal.tasks_number
        context['task_count'] = task_count
        return context

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(TaskCreate, self).form_valid(form)

    def get_success_url(self):
        if 'save_add' in self.request.POST:
            return reverse('proposals:task_create', args=(self.kwargs['pk'],))
        elif 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class TaskUpdate(UpdateView):
    model = Task
    form_class = TaskForm
    success_message = 'Taak bewerkt'

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        proposal = Task.objects.get(pk=self.kwargs['pk']).proposal
        task_count = proposal.task_set.count() + 1
        context['proposal'] = proposal
        context['save_add_button'] = task_count < proposal.tasks_number
        context['task_count'] = task_count - 1
        return context

    def get_success_url(self):
        task = Task.objects.get(pk=self.kwargs['pk'])
        if 'save_add' in self.request.POST:
            return reverse('proposals:task_create', args=(task.proposal.id,))
        elif 'save_continue' in self.request.POST:
            return self.object.proposal.continue_url()
        else:
            return reverse('proposals:my_concepts')


class TaskDelete(DeleteView):
    model = Task
    success_url = '/proposals/concepts/'
    success_message = 'Taak verwijderd'


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'
