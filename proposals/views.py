from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic

from .models import Proposal, Wmo, Study, Task, Member, Meeting, Faq
from .forms import WmoForm, StudyForm

# List views 
class ArchiveView(generic.ListView):
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
class DetailView(generic.DetailView):
    model = Proposal

# CRUD actions on Proposal
class ProposalCreate(SuccessMessageMixin, generic.CreateView): 
    model = Proposal
    fields = ('name', 'tech_summary', 'longitudinal', 'supervisor_name', 'supervisor_email', 'applicants')
    success_url = '/proposals/concepts/'
    success_message = 'Conceptaanvraag aangemaakt'

    def form_valid(self, form):
        form.instance.applicant = self.request.user
        form.instance.status = 0
        return super(ProposalCreate, self).form_valid(form)

class ProposalUpdate(SuccessMessageMixin, generic.UpdateView): 
    model = Proposal
    fields = ('name', 'tech_summary', 'longitudinal', 'supervisor_name', 'supervisor_email', 'applicants')
    success_url = '/proposals/concepts/'
    success_message = 'Conceptaanvraag bewerkt'

    def form_valid(self, form):
        form.instance.status = 0
        return super(ProposalUpdate, self).form_valid(form)

class ProposalDelete(SuccessMessageMixin, generic.DeleteView):
    model = Proposal
    success_url = '/proposals/concepts/'
    success_message = 'Aanvraag verwijderd'

# CRUD actions on Wmo
class WmoCreate(SuccessMessageMixin, generic.CreateView): 
    model = Wmo
    form_class = WmoForm
    success_url = '/proposals/concepts/'
    success_message = 'WMO-gegevens opgeslagen'

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(WmoCreate, self).form_valid(form)

# CRUD actions on a Study
class StudyCreate(SuccessMessageMixin, generic.CreateView): 
    model = Study
    form_class = StudyForm
    success_url = '/proposals/concepts/'
    success_message = 'Algemene kenmerken opgeslagen'

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).form_valid(form)

# CRUD actions on a Task
class TaskCreate(generic.CreateView):
    model = Task
    fields = ('name', 'procedure', 'duration', 'actions', 'registrations', 'registrations_details')

# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_user'] = self.request.user
        return context
