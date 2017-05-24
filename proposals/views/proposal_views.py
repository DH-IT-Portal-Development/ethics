# -*- encoding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from braces.views import GroupRequiredMixin, LoginRequiredMixin, UserFormKwargsMixin
from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView

from core.views import AllowErrorsMixin, CreateView, UpdateView, DeleteView
from core.utils import get_secretary
from reviews.utils import start_review

from ..copy import copy_proposal
from ..forms import ProposalForm, ProposalSubmitForm, ProposalConfirmationForm, \
    ProposalCopyForm, ProposalStartPracticeForm
from ..models import Proposal
from ..utils import generate_ref_number, generate_pdf, end_pre_assessment


############
# List views
############
class ProposalsView(LoginRequiredMixin, generic.ListView):
    title = _('Publiek archief')
    body = _('Dit overzicht toont alle goedgekeurde studies.')
    is_modifiable = False
    is_submitted = True
    context_object_name = 'proposals'

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon"""
        return Proposal.objects.filter(status__gte=Proposal.DECISION_MADE,
                                       status_review=True,
                                       in_archive=True)

    def get_context_data(self, **kwargs):
        context = super(ProposalsView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['body'] = self.body
        context['modifiable'] = self.is_modifiable
        context['submitted'] = self.is_submitted
        return context

    def get_my_proposals(self):
        return Proposal.objects.filter(Q(applicants=self.request.user) | Q(supervisor=self.request.user))


class MyConceptsView(ProposalsView):
    title = _('Mijn conceptstudies')
    body = _('Dit overzicht toont al uw nog niet ingediende studies.')
    is_modifiable = True
    is_submitted = False

    def get_queryset(self):
        """Returns all non-submitted Proposals for the current User"""
        return self.get_my_proposals().filter(status__lt=Proposal.SUBMITTED_TO_SUPERVISOR)


class MySubmittedView(ProposalsView):
    title = _('Mijn ingediende studies')
    body = _('Dit overzicht toont al uw ingediende studies.')
    is_modifiable = False
    is_submitted = True

    def get_queryset(self):
        """Returns all submitted Proposals for the current User"""
        return self.get_my_proposals().filter(status__gte=Proposal.SUBMITTED_TO_SUPERVISOR,
                                              status__lt=Proposal.DECISION_MADE)


class MyCompletedView(ProposalsView):
    title = _('Mijn afgehandelde studies')
    body = _('Dit overzicht toont al uw beoordeelde studies.')
    is_modifiable = False
    is_submitted = True

    def get_queryset(self):
        """Returns all completed Proposals for the current User"""
        return self.get_my_proposals().filter(status__gte=Proposal.DECISION_MADE)


class MyProposalsView(ProposalsView):
    title = _('Mijn studies')
    body = _('Dit overzicht toont al uw studies.')
    is_modifiable = True
    is_submitted = True

    def get_queryset(self):
        """Returns all Proposals for the current User"""
        return self.get_my_proposals()


class MyPracticeView(ProposalsView):
    title = _('Mijn oefenstudies')
    body = _('Dit overzicht toont alle oefenstudies waar u als student, \
onderzoeker of eindverantwoordelijke bij betrokken bent.')
    is_modifiable = True
    is_submitted = True

    def get_queryset(self):
        """Returns all practice Proposals for the current User"""
        return Proposal.objects.filter(Q(in_course=True) | Q(is_exploration=True),
                                       Q(applicants=self.request.user) |
                                       (Q(supervisor=self.request.user) &
                                        Q(status__gte=Proposal.SUBMITTED_TO_SUPERVISOR)))


##########################
# CRUD actions on Proposal
##########################
class ProposalMixin(UserFormKwargsMixin):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Studie %(title)s bewerkt')

    def get_next_url(self):
        proposal = self.object
        if hasattr(proposal, 'wmo'):
            return reverse('proposals:wmo_update', args=(proposal.pk,))
        else:
            return reverse('proposals:wmo_create', args=(proposal.pk,))


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

    def get_context_data(self, **kwargs):
        """Adds secretary and link to regulations to template context"""
        context = super(ProposalStart, self).get_context_data(**kwargs)
        context['secretary'] = get_secretary()
        context['regulations'] = 'https://etcl.wp.hum.uu.nl/reglement/'
        return context


class ProposalSubmit(AllowErrorsMixin, UpdateView):
    model = Proposal
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_message = _('Studie verzonden')

    def form_valid(self, form):
        """
        - Save the PDF on the Proposal
        - Start the review process on submission (though not for practice Proposals)
        """
        success_url = super(ProposalSubmit, self).form_valid(form)
        if 'save_back' not in self.request.POST:
            proposal = self.get_object()
            generate_pdf(proposal, 'proposals/proposal_pdf.html')
            if not proposal.is_practice():
                start_review(proposal)
        return success_url

    def get_next_url(self):
        return reverse('proposals:submitted', args=(self.object.pk,))

    def get_back_url(self):
        return reverse('studies:consent', args=(self.object.last_study().pk,))


class ProposalSubmitted(generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_submitted.html'


class ProposalConfirmation(GroupRequiredMixin, generic.UpdateView):
    model = Proposal
    template_name = 'proposals/proposal_confirmation.html'
    form_class = ProposalConfirmationForm
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        return reverse('reviews:my_archive')


class ProposalCopy(UserFormKwargsMixin, CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _('Studie gekopieerd')
    template_name = 'proposals/proposal_copy.html'

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        form.instance = copy_proposal(self, form)
        return super(ProposalCopy, self).form_valid(form)


class ProposalCopyRevision(ProposalCopy):
    def get_initial(self):
        """Sets initial value of is_revision to True"""
        initial = super(ProposalCopyRevision, self).get_initial()
        initial['is_revision'] = True
        return initial


class ProposalAsPdf(LoginRequiredMixin, PDFTemplateResponseMixin, generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_pdf.html'


class EmptyPDF(LoginRequiredMixin, PDFTemplateView):
    template_name = 'proposals/proposal_pdf_empty.html'


class ProposalDifference(LoginRequiredMixin, generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_diff.html'


########################
# Preliminary assessment
########################
class ProposalStartPreAssessment(ProposalStart):
    template_name = 'proposals/proposal_start_pre_assessment.html'


class PreAssessmentMixin(ProposalMixin):
    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(PreAssessmentMixin, self).get_form_kwargs()
        kwargs['is_pre_assessment'] = True
        return kwargs

    def get_next_url(self):
        proposal = self.object
        if hasattr(proposal, 'wmo'):
            return reverse('proposals:wmo_update_pre', args=(proposal.pk,))
        else:
            return reverse('proposals:wmo_create_pre', args=(proposal.pk,))


class ProposalCreatePreAssessment(PreAssessmentMixin, ProposalCreate):
    def form_valid(self, form):
        """Sets is_pre_assessment to True"""
        form.instance.is_pre_assessment = True
        return super(ProposalCreatePreAssessment, self).form_valid(form)


class ProposalUpdatePreAssessment(PreAssessmentMixin, ProposalUpdate):
    pass


class ProposalSubmitPreAssessment(ProposalSubmit):
    def form_valid(self, form):
        """
        Performs actions after saving the form
        - Save the preassessment PDF on the Proposal
        - End the preassessment phase
        """
        # Note that the below method does NOT call the ProposalSubmit method, as that would generate the full PDF.
        success_url = super(UpdateView, self).form_valid(form)
        if 'save_back' not in self.request.POST:
            proposal = self.get_object()
            generate_pdf(proposal, 'proposals/proposal_pdf_pre_assessment.html')
            end_pre_assessment(proposal)
        return success_url

    def get_next_url(self):
        return reverse('proposals:submitted_pre', args=(self.object.pk,))

    def get_back_url(self):
        return reverse('proposals:wmo_update_pre', args=(self.object.pk,))


class ProposalSubmittedPreAssessment(ProposalSubmitted):
    template_name = 'proposals/proposal_submitted.html'


##########
# Practice
##########
class ProposalStartPractice(generic.FormView):
    template_name = 'proposals/proposal_start_practice.html'
    form_class = ProposalStartPracticeForm

    def get_context_data(self, **kwargs):
        """Adds 'secretary', 'is_practice' and 'no_back' to template context"""
        context = super(ProposalStartPractice, self).get_context_data(**kwargs)
        context['secretary'] = get_secretary()
        context['is_practice'] = True
        context['no_back'] = True
        return context

    def get_success_url(self):
        """Go to the creation for a practice proposal"""
        return reverse('proposals:create_practice', args=(self.request.POST['practice_reason'],))


class ProposalCreatePractice(ProposalCreate):
    def get_context_data(self, **kwargs):
        """Adds 'is_practice' to template context"""
        context = super(ProposalCreatePractice, self).get_context_data(**kwargs)
        context['is_practice'] = True
        return context

    def get_form_kwargs(self):
        """Sets in_course as a form kwarg"""
        kwargs = super(ProposalCreatePractice, self).get_form_kwargs()
        kwargs['in_course'] = self.kwargs['reason'] == Proposal.COURSE
        return kwargs

    def form_valid(self, form):
        """Sets in_course and is_exploration"""
        form.instance.in_course = self.kwargs['reason'] == Proposal.COURSE
        form.instance.is_exploration = self.kwargs['reason'] == Proposal.EXPLORATION
        return super(ProposalCreatePractice, self).form_valid(form)


class ProposalUpdatePractice(ProposalUpdate):
    def get_form_kwargs(self):
        """Sets in_course as a form kwarg"""
        kwargs = super(ProposalUpdatePractice, self).get_form_kwargs()
        kwargs['in_course'] = self.object.in_course
        return kwargs
