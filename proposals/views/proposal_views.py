# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.views import generic
from django.utils.translation import ugettext as _

from easy_pdf.views import PDFTemplateResponseMixin

from .base_views import CreateView, UpdateView, DeleteView
from ..copy import copy_proposal
from ..forms import ProposalForm, ProposalCopyForm, UploadConsentForm, ProposalSubmitForm
from ..mixins import AllowErrorsMixin, LoginRequiredMixin
from ..models import Proposal
from ..utils import generate_ref_number
from reviews.utils import start_review


# List views
class ProposalsView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'proposals'

    def get_queryset(self):
        """Returns all the proposals that have been decided upon"""
        return Proposal.objects.filter(status__gte=Proposal.DECISION_MADE, allow_in_archive=True)

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

    def get_form_kwargs(self):
        kwargs = super(ProposalCopy, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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
