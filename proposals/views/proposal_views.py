# -*- encoding: utf-8 -*-

from braces.views import GroupRequiredMixin, LoginRequiredMixin, \
    UserFormKwargsMixin
from django.conf import settings
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView
from typing import Tuple, Union

from main.utils import get_document_contents, get_secretary, is_secretary
from main.views import AllowErrorsOnBackbuttonMixin, CreateView, DeleteView, \
    UpdateView, UserAllowedMixin
from observations.models import Observation
from proposals.utils.validate_proposal import get_form_errors
from reviews.mixins import CommitteeMixin, UsersOrGroupsAllowedMixin
from reviews.utils.review_utils import start_review, start_review_pre_assessment
from studies.models import Documents
from ..copy import copy_proposal
from ..forms import ProposalConfirmationForm, ProposalCopyForm, \
    ProposalDataManagementForm, ProposalForm, ProposalStartPracticeForm, \
    ProposalSubmitForm, RevisionProposalCopyForm, AmendmentProposalCopyForm
from ..models import Proposal, Wmo
from ..utils import generate_pdf, generate_ref_number
from proposals.mixins import ProposalMixin, ProposalContextMixin


############
# List views
############

class BaseProposalsView(LoginRequiredMixin, generic.TemplateView):
    title = _('Publiek archief')
    body = _('Dit overzicht toont alle goedgekeurde studies.')
    is_modifiable = False
    is_submitted = True
    contains_supervised = False
    template_name = 'proposals/proposal_list.html'

    def get_context_data(self, **kwargs):
        context = super(BaseProposalsView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['body'] = self.body
        context['modifiable'] = self.is_modifiable
        context['submitted'] = self.is_submitted
        context['supervised'] = self.contains_supervised
        context['data_url'] = None

        return context


class MyProposalsView(BaseProposalsView):
    title = _('Mijn studies')
    body = _('Dit overzicht toont al je studies.')
    is_modifiable = True
    is_submitted = True
    contains_supervised = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_archive',)
        return context


class MyConceptsView(BaseProposalsView):
    title = _('Mijn conceptstudies')
    body = _('Dit overzicht toont al je nog niet ingediende studies.')
    is_modifiable = True
    is_submitted = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_concepts',)
        return context


class MySubmittedView(BaseProposalsView):
    title = _('Mijn ingediende studies')
    body = _('Dit overzicht toont al je ingediende studies.')
    is_modifiable = False
    is_submitted = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_submitted',)
        return context


class MyCompletedView(BaseProposalsView):
    title = _('Mijn afgehandelde studies')
    body = _('Dit overzicht toont al je beoordeelde studies.')
    is_modifiable = False
    is_submitted = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_completed',)
        return context


class MySupervisedView(BaseProposalsView):
    title = _('Mijn studies als eindverantwoordelijke')
    body = _(
        'Dit overzicht toont al je studies waarvan je eindverantwoordelijke '
        'bent.')
    is_modifiable = True
    is_submitted = True
    contains_supervised = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_supervised',)
        return context

class MyPracticeView(BaseProposalsView):
    title = _('Mijn oefenstudies')
    body = _('Dit overzicht toont alle oefenstudies waar je als student, \
onderzoeker of eindverantwoordelijke bij betrokken bent.')
    is_modifiable = True
    is_submitted = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_practice',)
        return context


class ProposalArchiveView(CommitteeMixin, BaseProposalsView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:archive', args=[self.committee])
        return context

    @property
    def title(self):
        return "{} - {}".format(
            _('Publiek archief'),
            self.committee_display_name
        )


class ProposalsExportView(GroupRequiredMixin, generic.ListView):
    context_object_name = 'proposals'
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER
    ]
    template_name_suffix = '_export_list'

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon,
        or a single one if specified in the URL"""
        pk = self.kwargs.get('pk')

        if pk is not None:
            return Proposal.objects.filter(pk=pk)

        return Proposal.objects.filter(status__gte=Proposal.DECISION_MADE,
                                       status_review=True,
                                       in_archive=True).order_by(
            "-date_reviewed"
        )


class HideFromArchiveView(GroupRequiredMixin, generic.RedirectView):
    group_required = settings.GROUP_SECRETARY
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')

        proposal = Proposal.objects.get(pk=pk)
        proposal.public = False
        proposal.save()

        return reverse('proposals:archive')

##########################
# CRUD actions on Proposal
##########################

class ProposalCreate(ProposalMixin, AllowErrorsOnBackbuttonMixin, CreateView):
    def get_initial(self):
        """Sets initial applicant to current User"""
        initial = super(ProposalCreate, self).get_initial()
        initial['applicants'] = [self.request.user]
        return initial

    def form_valid(self, form):
        """Sets created_by to current user and generates a reference number"""
        form.instance.created_by = self.request.user
        form.instance.reference_number = generate_ref_number()
        form.instance.reviewing_committee = form.instance.institution.reviewing_chamber
        return super(ProposalCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Adds 'create'/'no_back' to template context"""
        context = super(ProposalCreate, self).get_context_data(**kwargs)
        context['create'] = True
        context['no_back'] = True
        return context


class ProposalUpdate(ProposalMixin, ProposalContextMixin, AllowErrorsOnBackbuttonMixin, UpdateView):

    def form_valid(self, form):
        """Sets created_by to current user and generates a reference number"""
        form.instance.reviewing_committee = form.instance.institution.reviewing_chamber
        return super(ProposalUpdate, self).form_valid(form)

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
        """After deletion, return to the concepts overview"""
        return reverse('proposals:my_concepts')


class CompareDocumentsView(UsersOrGroupsAllowedMixin, generic.TemplateView):
    template_name = 'proposals/compare_documents.html'
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    def get_allowed_users(self):

        compare_type = self.kwargs.get('type')
        new_pk = self.kwargs.get('new')
        attribute = self.kwargs.get('attribute')

        model = {
            'documents': Documents,
            'wmo': Wmo,
            'observation': Observation,
            'proposal': Proposal,
        }.get(compare_type, None)

        if model == Proposal:
            proposal = Proposal.objects.get(pk=new_pk)
        else:
            proposal = model.objects.get(pk=new_pk).proposal

        allowed_users = list(proposal.applicants.all())
        if proposal.supervisor:
            allowed_users.append(proposal.supervisor)

        return allowed_users


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        old_file, new_file = self._get_files()

        context['old_name'] = old_file.name
        context['old_text'] = get_document_contents(old_file)
        context['new_name'] = new_file.name
        context['new_text'] = get_document_contents(new_file)

        return context


    def _get_files(self) -> Tuple[
        Union[None, FieldFile],
        Union[None, FieldFile]
    ]:
        compare_type = self.kwargs.get('type')
        old_pk = self.kwargs.get('old')
        new_pk = self.kwargs.get('new')
        attribute = self.kwargs.get('attribute')

        model = {
            'documents': Documents,
            'wmo': Wmo,
            'observation': Observation,
            'proposal': Proposal,
        }.get(compare_type, None)

        if model is None:
            return None, None

        old = model.objects.get(pk=old_pk)
        new = model.objects.get(pk=new_pk)

        return getattr(old, attribute, None), getattr(new, attribute, None)


###########################
# Other actions on Proposal
###########################
class ProposalStart(generic.TemplateView):
    template_name = 'proposals/proposal_start.html'

    def get_context_data(self, **kwargs):
        """Adds secretary and link to regulations to template context"""
        context = super(ProposalStart, self).get_context_data(**kwargs)
        context['secretary'] = get_secretary()
        return context


class ProposalDataManagement(UpdateView):
    model = Proposal
    form_class = ProposalDataManagementForm
    template_name = 'proposals/proposal_data_management.html'

    def get_next_url(self):
        """Continue to the submission view"""
        return reverse('proposals:submit', args=(self.object.pk,))

    def get_back_url(self):
        """Return to the consent form overview of the last Study"""
        return reverse('proposals:consent', args=(self.object.pk,))


class ProposalSubmit(ProposalContextMixin, AllowErrorsOnBackbuttonMixin, UpdateView, ):
    model = Proposal
    form_class = ProposalSubmitForm
    template_name = 'proposals/proposal_submit.html'
    success_message = _('Wijzigingen opgeslagen')

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(ProposalSubmit, self).get_form_kwargs()
        kwargs['proposal'] = self.get_object()

        # Required for examining POST data
        # to check for js-redirect-submit
        kwargs['request'] = self.request

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProposalSubmit, self).get_context_data(**kwargs)

        context['troublesome_pages'] = get_form_errors(self.get_object())
        context['pagenr'] = self._get_page_number()
        context['is_supervisor_edit_phase'] = self.is_supervisor_edit_phase()

        return context

    def is_supervisor_edit_phase(self):
        if self.object.status == self.object.SUBMITTED_TO_SUPERVISOR:
            return True

        return False

    def form_valid(self, form):
        """
        - Save the PDF on the Proposal
        - Start the review process on submission (though not for practice Proposals)
        """

        success_url = super(ProposalSubmit, self).form_valid(form)
        if 'save_back' not in self.request.POST and 'js-redirect-submit' not in self.request.POST:
            proposal = self.get_object()
            generate_pdf(proposal, 'proposals/proposal_pdf.html')
            if not proposal.is_practice() and proposal.status == Proposal.DRAFT:
                start_review(proposal)
        return success_url

    def get_next_url(self):
        """After submission, go to the thank-you view. Unless a supervisor is
        editing the proposal during their review, in that case: go to their
        decide page"""
        if self.is_supervisor_edit_phase() and \
                self.current_user_is_supervisor():
            review = self.object.latest_review()
            decision = review.decision_set.get(reviewer=self.request.user)
            return reverse('reviews:decide', args=(decision.pk,))

        return reverse('proposals:submitted', args=(self.object.pk,))

    def get_back_url(self):
        """Return to the data management view"""
        return reverse('proposals:data_management', args=(self.object.pk,))

    def _get_page_number(self):
        if self.object.is_pre_assessment:
            return 3

        if self.object.is_pre_approved:
            return 2

        return 6


class ProposalSubmitted(generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_submitted.html'


class ProposalConfirmation(GroupRequiredMixin, generic.UpdateView):
    model = Proposal
    template_name = 'proposals/proposal_confirmation.html'
    form_class = ProposalConfirmationForm
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        """On confirmation, return to the Review archive"""
        committee = self.object.reviewing_committee.name
        return reverse('reviews:my_archive', args=[committee])


class ProposalCopy(UserFormKwargsMixin, CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _('Studie gekopieerd')
    template_name = 'proposals/proposal_copy.html'

    def get_initial(self):
        """Sets initial value of is_revision to False. It's a hidden field,
        so this value will also be the actual value. Used for the different
        behaviour for this class' subclasses
        """
        initial = super(ProposalCopy, self).get_initial()
        initial['is_revision'] = False
        return initial

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        form.instance = copy_proposal(self, form)
        return super(ProposalCopy, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_revision'] = False
        context['is_amendment'] = False

        return context


class ProposalCopyRevision(ProposalCopy):
    form_class = RevisionProposalCopyForm

    def get_initial(self):
        """Sets initial value of is_revision to True"""
        initial = super(ProposalCopyRevision, self).get_initial()
        initial['is_revision'] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_revision'] = True

        return context


class ProposalCopyAmendment(ProposalCopy):
    form_class = AmendmentProposalCopyForm

    def get_initial(self):
        """Sets initial value of is_revision to True"""
        initial = super(ProposalCopyAmendment, self).get_initial()
        initial['is_revision'] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_amendment'] = True

        return context


class ProposalAsPdf(LoginRequiredMixin, PDFTemplateResponseMixin,
                    generic.DetailView):
    model = Proposal
    template_name = 'proposals/proposal_pdf.html'

    def get_context_data(self, **kwargs):
        """Adds 'BASE_URL' to template context"""
        context = super(ProposalAsPdf, self).get_context_data(**kwargs)
        context['BASE_URL'] = settings.BASE_URL

        if self.object.is_pre_approved:
            self.template_name = 'proposals/proposal_pdf_pre_approved.html'
        elif self.object.is_pre_assessment:
            self.template_name = 'proposals/proposal_pdf_pre_assessment.html'

        documents = {
            'extra': []
        }

        for document in Documents.objects.filter(proposal=self.object).all():
            if document.study:
                documents[document.study.pk] = document
            else:
                documents['extra'].append(document)

        context['documents'] = documents

        return context


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
        """Sets is_pre_assessment as a form kwarg"""
        kwargs = super(PreAssessmentMixin, self).get_form_kwargs()
        kwargs['is_pre_assessment'] = True
        return kwargs

    def get_next_url(self):
        """If the Proposal has a Wmo model attached, go to update, else, go to create"""
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
        success_url = super(ProposalSubmitPreAssessment, self).form_valid(form)
        if 'save_back' not in self.request.POST and 'js-redirect-submit' not in self.request.POST:
            proposal = self.get_object()
            generate_pdf(proposal, 'proposals/proposal_pdf_pre_assessment.html')
            start_review_pre_assessment(proposal)
        return success_url

    def get_next_url(self):
        """After submission, go to the thank-you view"""
        return reverse('proposals:submitted_pre', args=(self.object.pk,))

    def get_back_url(self):
        """Return to the Wmo overview"""
        return reverse('proposals:wmo_update_pre', args=(self.object.pk,))


class ProposalSubmittedPreAssessment(ProposalSubmitted):
    template_name = 'proposals/proposal_submitted.html'


#############
# Pre-Aproved
#############

class ProposalStartPreApproved(ProposalStart):
    template_name = 'proposals/proposal_start_pre_approved.html'


class PreApprovedMixin(ProposalMixin):
    def get_form_kwargs(self):
        """Sets is_pre_approved as a form kwarg"""
        kwargs = super(PreApprovedMixin, self).get_form_kwargs()
        kwargs['is_pre_approved'] = True
        return kwargs

    def get_next_url(self):
        proposal = self.object
        return reverse('proposals:submit_pre_approved', args=(proposal.pk,))


class ProposalCreatePreApproved(PreApprovedMixin, ProposalCreate):
    template_name = 'proposals/proposal_form_pre_approved.html'

    def form_valid(self, form):
        """Sets is_pre_approved to True"""
        form.instance.is_pre_approved = True
        return super(ProposalCreatePreApproved, self).form_valid(form)


class ProposalUpdatePreApproved(PreApprovedMixin, ProposalUpdate):
    pass


class ProposalSubmitPreApproved(ProposalSubmit):
    def form_valid(self, form):
        """
        Performs actions after saving the form
        - Save the pre_approved PDF on the Proposal
        - End the draft phase and start the appropiate review phase (in super function)
        """
        success_url = super(ProposalSubmitPreApproved, self).form_valid(form)
        if 'save_back' not in self.request.POST:
            proposal = self.get_object()
            generate_pdf(proposal, 'proposals/proposal_pdf_pre_approved.html')
        return success_url

    def get_next_url(self):
        """After submission, go to the thank-you view"""
        return reverse('proposals:submitted_pre_approved',
                       args=(self.object.pk,))

    def get_back_url(self):
        """Return to the update page"""
        return reverse('proposals:update_pre_approved', args=(self.object.pk,))


class ProposalSubmittedPreApproved(ProposalSubmitted):
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
        """Go to the creation for a practice Proposal"""
        return reverse('proposals:create_practice',
                       args=(self.request.POST['practice_reason'],))


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
        form.instance.is_exploration = self.kwargs[
                                           'reason'] == Proposal.EXPLORATION
        return super(ProposalCreatePractice, self).form_valid(form)


class ProposalUpdatePractice(ProposalUpdate):
    def get_form_kwargs(self):
        """Sets in_course as a form kwarg"""
        kwargs = super(ProposalUpdatePractice, self).get_form_kwargs()
        kwargs['in_course'] = self.object.in_course
        return kwargs
