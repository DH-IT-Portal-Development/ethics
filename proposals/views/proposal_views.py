# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.views import generic
from django.utils.translation import ugettext as _

from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView

from .base_views import CreateView, UpdateView, DeleteView
from ..copy import copy_proposal
from ..forms import ProposalForm, ProposalCopyForm, ProposalSubmitForm
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
        return _('Publiek archief')

    def get_body(self):
        return _('Dit overzicht toont alle beoordeelde studies.')


class MyConceptsView(ProposalsView):
    def get_queryset(self):
        """Returns all non-submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__lt=Proposal.SUBMITTED_TO_SUPERVISOR)

    def get_title(self):
        return _('Mijn conceptstudies')

    def get_body(self):
        return _('Dit overzicht toont al uw nog niet ingediende studies.')


class MySubmittedView(ProposalsView):
    def get_queryset(self):
        """Returns all submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.SUBMITTED_TO_SUPERVISOR, status__lt=Proposal.DECISION_MADE)

    def get_title(self):
        return _('Mijn ingediende studies')

    def get_body(self):
        return _('Dit overzicht toont al uw ingediende studies.')


class MyCompletedView(ProposalsView):
    def get_queryset(self):
        """Returns all completed proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.DECISION_MADE)

    def get_title(self):
        return _('Mijn afgeronde studies')

    def get_body(self):
        return _('Dit overzicht toont al uw beoordeelde studies.')


class MyProposalsView(ProposalsView):
    def get_queryset(self):
        """Returns all proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user)

    def get_title(self):
        return _('Mijn studies')

    def get_body(self):
        return _('Dit overzicht toont al uw studies.')


##########################
# CRUD actions on Proposal
##########################
class DetailView(LoginRequiredMixin, generic.DetailView):
    # TODO: limit access to applicants, supervisor and commission
    model = Proposal


class ProposalMixin(object):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Studie %(title)s bewerkt')

    def get_form_kwargs(self):
        """Sets the User as a form kwarg"""
        kwargs = super(ProposalMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_next_url(self):
        proposal = self.object
        if hasattr(proposal, 'wmo'):
            return reverse('proposals:wmo_update', args=(proposal.id,))
        else:
            return reverse('proposals:wmo_create', args=(proposal.id,))


class ProposalCreate(ProposalMixin, AllowErrorsMixin, CreateView):
    def get_initial(self):
        """Sets initial applicant to current User"""
        initial = super(ProposalCreate, self).get_initial()
        initial['applicants'] = [self.request.user]
        return initial

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


class ProposalUpdate(ProposalMixin, AllowErrorsMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Studie %(title)s bewerkt')

    def get_context_data(self, **kwargs):
        """Adds 'create'/'no_back' to template context"""
        context = super(ProposalUpdate, self).get_context_data(**kwargs)
        context['create'] = False
        context['no_back'] = True
        return context


class ProposalDelete(DeleteView):
    model = Proposal
    success_message = _('Studie verwijderd')

    def get_success_url(self):
        return reverse('proposals:my_concepts')


###########################
# Other actions on Proposal
###########################
class ProposalStart(generic.TemplateView):
    template_name = 'proposals/proposal_start.html'


class ProposalCopy(CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _('Studie gekopieerd')
    template_name = 'proposals/proposal_copy.html'

    def get_form_kwargs(self):
        kwargs = super(ProposalCopy, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        form.instance = copy_proposal(self, form)
        return super(ProposalCopy, self).form_valid(form)


class ProposalSubmit(UpdateView):
    model = Proposal
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_message = _('Studie verzonden')

    def form_valid(self, form):
        """Start the review process on submission"""
        success_url = super(ProposalSubmit, self).form_valid(form)
        if 'save_back' not in self.request.POST:
            start_review(self.get_object())
        return success_url

    def get_next_url(self):
        return reverse('proposals:my_submitted')

    def get_back_url(self):
        return reverse('proposals:study_survey', args=(self.object.study.pk,))


class ProposalAsPdf(LoginRequiredMixin, PDFTemplateResponseMixin, generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_pdf.html'


class EmptyPDF(LoginRequiredMixin, PDFTemplateView):
    template_name = 'proposals/proposal_pdf_empty.html'
