# -*- encoding: utf-8 -*-

import datetime

from braces.views import GroupRequiredMixin, LoginRequiredMixin, \
    UserFormKwargsMixin

from django.conf import settings
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
#from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView
from typing import Any, Tuple, Union

from main.utils import get_document_contents, get_secretary, is_secretary
from main.views import AllowErrorsOnBackbuttonMixin, CreateView, DeleteView, \
    UpdateView, UserAllowedMixin
from observations.models import Observation
from proposals.utils.validate_proposal import get_form_errors
from proposals.utils.pdf_diff_logic import *
from reviews.mixins import CommitteeMixin, UsersOrGroupsAllowedMixin
from reviews.utils.review_utils import start_review, start_review_pre_assessment
from studies.models import Documents
from ..copy import copy_proposal
from ..forms import ProposalConfirmationForm, ProposalCopyForm, \
    ProposalDataManagementForm, ProposalForm, ProposalStartPracticeForm, \
    ProposalSubmitForm, RevisionProposalCopyForm, AmendmentProposalCopyForm, \
    ProposalUpdateDataManagementForm, TranslatedConsentForms
from ..models import Proposal, Wmo
from ..utils import generate_pdf, generate_ref_number
from proposals.mixins import ProposalMixin, ProposalContextMixin, \
    PDFTemplateResponseMixin
from proposals.utils.proposal_utils import FilenameFactory


############
# List views
############

class BaseProposalsView(LoginRequiredMixin, generic.TemplateView):
    title = _('Publiek archief')
    body = _('Dit overzicht toont alle goedgekeurde aanvragen.')
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
    title = _('Mijn aanvraag')
    body = _('Dit overzicht toont al je aanvragen.')
    is_modifiable = True
    is_submitted = True
    contains_supervised = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_archive',)
        return context


class MyConceptsView(BaseProposalsView):
    title = _('Mijn conceptaanvragen')
    body = _('Dit overzicht toont al je nog niet ingediende aanvragen.')
    is_modifiable = True
    is_submitted = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_concepts',)
        return context


class MySubmittedView(BaseProposalsView):
    title = _('Mijn ingediende aanvragen')
    body = _('Dit overzicht toont al je ingediende aanvragen.')
    is_modifiable = False
    is_submitted = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_submitted',)
        return context


class MyCompletedView(BaseProposalsView):
    title = _('Mijn afgehandelde aanvragen')
    body = _('Dit overzicht toont al je beoordeelde aanvragen.')
    is_modifiable = False
    is_submitted = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_completed',)
        return context


class MySupervisedView(BaseProposalsView):
    title = _('Mijn aanvragen als eindverantwoordelijke')
    body = _(
        'Dit overzicht toont alle aanvragen waarvan je eindverantwoordelijke '
        'bent.')
    is_modifiable = True
    is_submitted = True
    contains_supervised = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_supervised',)
        return context

class MyPracticeView(BaseProposalsView):
    title = _('Mijn oefenaanvragen')
    body = _('Dit overzicht toont alle oefenaanvragen waar je als student, \
onderzoeker of eindverantwoordelijke bij betrokken bent.')
    is_modifiable = True
    is_submitted = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:my_practice',)
        return context


class ProposalUsersOnlyArchiveView(CommitteeMixin, BaseProposalsView):
    template_name = 'proposals/proposal_private_archive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_url'] = reverse('proposals:api:archive', args=[self.committee])
        return context

    @property
    def title(self):
        return "{} - {}".format(
            _('Archief'),
            self.committee_display_name
        )


class ProposalsPublicArchiveView(generic.ListView):
    template_name = "proposals/proposal_public_archive.html"
    model = Proposal

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon"""
        return Proposal.objects.public_archive()

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

        return Proposal.objects.export()


class ChangeArchiveStatusView(GroupRequiredMixin, generic.RedirectView):
    group_required = settings.GROUP_SECRETARY
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get('pk')

        proposal = Proposal.objects.get(pk=pk)
        proposal.in_archive = not proposal.in_archive
        proposal.save()
        committee = proposal.reviewing_committee.name
        return reverse('proposals:archive', args=[committee])

##########################
# CRUD actions on Proposal
##########################

class ProposalCreate(ProposalMixin, AllowErrorsOnBackbuttonMixin, CreateView):

    # Note: template_name is auto-generated to proposal_form.html

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
    success_message = _('Aanvraag verwijderd')

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

        self.old_file, self.new_file = self._get_files()

        context['old_name'] = self.old_file.name
        context['old_file'] = self.old_file
        context['old_text'] = get_document_contents(self.old_file)
        context['new_name'] = self.new_file.name
        context['new_file'] = self.new_file
        context['new_text'] = get_document_contents(self.new_file)

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
    
class TranslatedConsentFormsView(UpdateView):
    model = Proposal
    form_class = TranslatedConsentForms
    template_name = 'proposals/translated_consent_forms.html'

    def get_next_url(self):
        '''Go to the consent form upload page'''
        return reverse('proposals:consent', args=(self.object.pk,))

    def get_back_url(self):
        """Return to the overview of the last Study"""
        return reverse('studies:design_end', args=(self.object.last_study().pk,))


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


class ProposalUpdateDataManagement(GroupRequiredMixin, generic.UpdateView):
    """
    Allows the secretary to change the Data Management Plan on the Proposal level
    """
    model = Proposal
    template_name = 'proposals/proposal_update_attachments.html'
    form_class = ProposalUpdateDataManagementForm
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        """Continue to the URL specified in the 'next' POST parameter"""
        return reverse('reviews:detail', args=[self.object.latest_review().pk])


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
        context['start_date_warning'] = self.check_start_date()

        return context

    def check_start_date(self):
        """
        Return true if the proposal's intended start date lies within
        two weeks of today.
        """
        start_date = self.object.date_start
        if not start_date:
            return False
        two_weeks = datetime.timedelta(days=14)
        two_weeks_from_now = datetime.date.today() + two_weeks
        return start_date <= two_weeks_from_now

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
        return reverse('proposals:data_management', aPdfrgs=(self.object.pk,))

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
    success_message = _('Aanvraag gekopieerd')
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
        form.instance = copy_proposal(
            form.cleaned_data['parent'],
            form.cleaned_data['is_revision'],
            self.request.user,
        )
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

    # The PDF mixin generates a filename with this factory
    filename_factory = FilenameFactory('Proposal')

    def get_context_data(self, **kwargs):
        """Adds 'BASE_URL' to template context"""
        context = super(ProposalAsPdf, self).get_context_data(**kwargs)

        context['general'] = GeneralSection(self.object)
        context['wmo'] = WMOSection(self.object.wmo)
        if self.object.wmo.status != self.object.wmo.NO_WMO:
            context['metc'] = METCSection(self.object.wmo)
        context['trajectories'] = TrajectoriesSection(self.object)
        if self.object.wmo.status == self.object.wmo.NO_WMO:
            context['studies'] = []
            for study in self.object.study_set.all():
                study_sections = []
                study_sections.append(StudySection(study))
                if study.has_intervention:
                    study_sections.append(InterventionSection(study.intervention))
                if study.has_observation:
                    study_sections.append(ObservationSection(study.observation))
                if study.has_sessions:
                    study_sections.append(SessionsSection(study))
                    for session in study.session_set.all():
                        study_sections.append(SessionSection(session))
                        for task in session.task_set.all():
                            study_sections.append(TaskSection(task))
                    study_sections.append(TasksOverviewSection(session))
                study_sections.append(StudyOverviewSection(study))
                study_sections.append(InformedConsentFormsSection(study.documents))
                context['studies'].append(study_sections)
        extra_documents = []
        for count, document in enumerate(Documents.objects.filter(
            proposal = self.object,
            study__isnull = True
        )):
            extra_documents.append(ExtraDocumentsSection(document, count+1))
        if extra_documents:
            context['extra_documents'] = extra_documents
        if self.object.dmp_file:
            context['dmp_file'] = DMPFileSection(self.object)
        context['embargo'] = EmbargoSection(self.object)

        return context


class ProposalDifference(LoginRequiredMixin, generic.DetailView):
    model = Proposal
    template_name = 'proposals/new_proposal_diff.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general'] = GeneralSection(self.object.parent, self.object)
        return context

class NewPDFViewTest(generic.TemplateView):

    template_name = 'proposals/pdf/new_pdf_test.html'

    def get_context_data(self, **kwargs):
        model = Proposal.objects.last()
        context = super().get_context_data(**kwargs)

        context = create_context_pdf_diff(context, model)
               
        return context



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
