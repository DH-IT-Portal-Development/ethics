from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import generic
from django.core.urlresolvers import reverse

from .models import Proposal, Wmo, Study, Task, Member, Meeting, Faq
from .forms import ProposalForm, WmoForm, StudyForm, TaskStartForm, TaskForm, TaskEndForm, UploadConsentForm, ProposalSubmitForm


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


# List views
class ArchiveView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'proposals'

    def get_queryset(self):
        """Return all the proposals"""
        return Proposal.objects.all()


class IndexView(ArchiveView):
    def get_queryset(self):
        """Return all the proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status=6)


class ConceptsView(ArchiveView):
    def get_queryset(self):
        """Return all the proposals for the current user with status concept"""
        return Proposal.objects.filter(applicants=self.request.user)


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
    success_url = '/proposals/concepts/'
    success_message = 'Conceptaanvraag aangemaakt'

    def get_initial(self):
        return {'applicants': [self.request.user]}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(ProposalCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProposalCreate, self).get_context_data(**kwargs)
        context['create'] = True
        return context


class ProposalUpdate(UpdateView):
    model = Proposal
    form_class = ProposalForm
    success_url = '/proposals/concepts/'
    success_message = 'Conceptaanvraag bewerkt'


class ProposalTaskStart(UpdateView):
    model = Proposal
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_url = '/proposals/concepts/'
    success_message = ''


class ProposalTaskEnd(UpdateView):
    model = Proposal
    form_class = TaskEndForm
    template_name = 'proposals/task_end.html'
    success_url = '/proposals/concepts/'
    success_message = ''


class ProposalUploadConsent(UpdateView):
    model = Proposal
    form_class = UploadConsentForm
    template_name = 'proposals/proposal_consent.html'
    success_url = '/proposals/concepts/'
    success_message = 'Informed consent geupload'


class ProposalSubmit(UpdateView):
    model = Proposal
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_url = '/proposals/concepts/'
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
    success_url = '/proposals/concepts/'
    success_message = 'WMO-gegevens opgeslagen'

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(WmoCreate, self).form_valid(form)


class WmoUpdate(UpdateView):
    model = Wmo
    form_class = WmoForm
    success_url = '/proposals/concepts/'
    success_message = 'WMO-gegevens bewerkt'


# CRUD actions on a Study
class StudyCreate(CreateView):
    model = Study
    form_class = StudyForm
    success_url = '/proposals/concepts/'
    success_message = 'Algemene kenmerken opgeslagen'

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).form_valid(form)


class StudyUpdate(UpdateView):
    model = Study
    form_class = StudyForm
    success_url = '/proposals/concepts/'
    success_message = 'Algemene kenmerken bewerkt'


# CRUD actions on a Task
class TaskCreate(CreateView):
    model = Task
    form_class = TaskForm
    success_message = 'Taak opgeslagen'

    def get_context_data(self, **kwargs):
        context = super(TaskCreate, self).get_context_data(**kwargs)
        proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        context['proposal'] = proposal
        context['save_add_button'] = proposal.task_set.count() + 1 < proposal.tasks_number
        return context

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(TaskCreate, self).form_valid(form)

    def get_success_url(self):
        if 'save_add' in self.request.POST:
            return reverse('proposals:task_create', args=(self.kwargs['pk'],))
        else:
            return reverse('proposals:my_concepts')


class TaskUpdate(UpdateView):
    model = Task
    form_class = TaskForm
    success_message = 'Taak bewerkt'

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        proposal = Task.objects.get(pk=self.kwargs['pk']).proposal
        context['proposal'] = proposal
        context['save_add_button'] = proposal.task_set.count() + 1 < proposal.tasks_number
        return context

    def get_success_url(self):
        task = Task.objects.get(pk=self.kwargs['pk'])
        if 'save_add' in self.request.POST:
            return reverse('proposals:task_create', args=(task.proposal.id,))
        else:
            return reverse('proposals:my_concepts')


class TaskDelete(DeleteView):
    model = Task
    success_url = '/proposals/concepts/'
    success_message = 'Taak verwijderd'


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_user'] = self.request.user
        return context
