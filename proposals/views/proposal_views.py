# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.views import generic
from django.utils.translation import ugettext as _

from braces.views import LoginRequiredMixin
from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView

from core.views import AllowErrorsMixin, CreateView, UpdateView, DeleteView
from reviews.utils import start_review

from ..copy import copy_proposal
from ..forms import ProposalForm, ProposalConsentForm, ProposalSubmitForm, ProposalCopyForm
from ..models import Proposal
from ..utils import generate_ref_number


# List views
class ProposalsView(LoginRequiredMixin, generic.ListView):
    title = _('Publiek archief')
    body = _('Dit overzicht toont alle beoordeelde studies.')
    is_modifiable = False
    is_submitted = True
    context_object_name = 'proposals'

    def get_queryset(self):
        """Returns all the proposals that have been decided upon, TODO: with a positive Review"""
        return Proposal.objects.filter(status__gte=Proposal.DECISION_MADE)

    def get_context_data(self, **kwargs):
        context = super(ProposalsView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['body'] = self.body
        context['modifiable'] = self.is_modifiable
        context['submitted'] = self.is_submitted
        return context


class MyConceptsView(ProposalsView):
    title = _('Mijn conceptstudies')
    body = _('Dit overzicht toont al uw nog niet ingediende studies.')
    is_modifiable = True
    is_submitted = False

    def get_queryset(self):
        """Returns all non-submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__lt=Proposal.SUBMITTED_TO_SUPERVISOR)


class MySubmittedView(ProposalsView):
    title = _('Mijn ingediende studies')
    body = _('Dit overzicht toont al uw ingediende studies.')
    is_modifiable = False
    is_submitted = True

    def get_queryset(self):
        """Returns all submitted proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.SUBMITTED_TO_SUPERVISOR, status__lt=Proposal.DECISION_MADE)


class MyCompletedView(ProposalsView):
    title = _('Mijn afgeronde studies')
    body = _('Dit overzicht toont al uw beoordeelde studies.')
    is_modifiable = False
    is_submitted = True

    def get_queryset(self):
        """Returns all completed proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user).filter(status__gte=Proposal.DECISION_MADE)


class MyProposalsView(ProposalsView):
    title = _('Mijn studies')
    body = _('Dit overzicht toont al uw studies.')
    is_modifiable = True
    is_submitted = True

    def get_queryset(self):
        """Returns all proposals for the current user"""
        return Proposal.objects.filter(applicants=self.request.user)


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


class ProposalConsent(AllowErrorsMixin, UpdateView):
    """
    Allows the applicant to add informed consent to their Proposal
    """
    model = Proposal
    form_class = ProposalConsentForm
    success_message = _('Consent opgeslagen')
    template_name = 'proposals/proposal_consent.html'

    def get_next_url(self):
        return reverse('proposals:study_design', args=(self.kwargs['pk'],))

    def get_back_url(self):
        return reverse('proposals:study_update', args=(self.kwargs['pk'],))


class ProposalSubmit(AllowErrorsMixin, UpdateView):
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
        return reverse('proposals:submitted')

    def get_back_url(self):
        return reverse('proposals:study_survey', args=(self.object.study.pk,))


class ProposalSubmitted(generic.TemplateView):
    template_name = 'proposals/proposal_submitted.html'


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


class ProposalAsPdf(LoginRequiredMixin, PDFTemplateResponseMixin, generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_pdf.html'


class EmptyPDF(LoginRequiredMixin, PDFTemplateView):
    template_name = 'proposals/proposal_pdf_empty.html'


class ProposalDifference(LoginRequiredMixin, generic.TemplateView):
    template_name = 'proposals/proposal_diff.html'
