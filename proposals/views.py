from django.http import HttpResponseRedirect
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic
from django.shortcuts import render_to_response

from .models import Proposal, Wmo, ParticipantGroup
from .forms import ProposalForm

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

class ProposalDelete(generic.DeleteView):
    model = Proposal
    success_url = '/proposals/concepts/'

# CRUD actions on Wmo
class WmoCreate(generic.CreateView): 
    model = Wmo
    fields = ('metc', 'metc_institution', 'is_medical', 'is_behavioristic', 'metc_decision', 'metc_decision_pdf')
    success_url = '/proposals/concepts/'

    def form_valid(self, form):
        form.instance.status = 1
        return super(WmoCreate, self).form_valid(form)

# CRUD actions on a Study
class StudyCreate(generic.CreateView): 
    model = ParticipantGroup
    fields = ('age_groups', 'traits', 'necessity', 'necessity_reason', 'setting', 'setting_details', \
        'risk_physical', 'risk_psychological', 'compensation', 'recruitment')
    success_url = '/proposals/concepts/'

    def form_valid(self, form):
        form.instance.status = 2
        return super(StudyCreate, self).form_valid(form)

# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_user'] = self.request.user
        return context

# Actions... to be deleted?
def add_proposal(request): 
    if request.method == 'POST':
        form = ProposalForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = ProposalForm()

    return render_to_response('proposals/add_proposal.html', {'form': form})

def save_proposal(form_list, request): 
    proposal = Proposal()
    for form in form_list: 
        for field, value in form.cleaned_data.iteritems():
            setattr(proposal, field, value)
    proposal.applicant = request.user
    proposal.save()

class ApplicationWizard(SessionWizardView):
    #file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'informed_consent'))

    def done(self, form_list, **kwargs):
        save_proposal(form_list, self.request) # TODO
        return HttpResponseRedirect('/proposals/')
