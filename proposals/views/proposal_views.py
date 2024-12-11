# -*- encoding: utf-8 -*-

import datetime

from braces.views import GroupRequiredMixin, LoginRequiredMixin, UserFormKwargsMixin

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.http import FileResponse, HttpResponseRedirect

# from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView
from typing import Tuple, Union

from main.utils import get_document_contents, get_secretary, is_secretary
from main.views import (
    AllowErrorsOnBackbuttonMixin,
    CreateView,
    DeleteView,
    HumanitiesOrPrivilegeRequiredMixin,
    UpdateView,
)
from observations.models import Observation
from proposals.utils.pdf_diff_logic import create_context_pdf, create_context_diff
from reviews.mixins import CommitteeMixin, UsersOrGroupsAllowedMixin
from reviews.utils.review_utils import start_review, start_review_pre_assessment
from studies.models import Documents
from attachments.models import Attachment, StudyAttachment, ProposalAttachment
from ..copy import copy_proposal
from ..forms import (
    ProposalConfirmationForm,
    ProposalCopyForm,
    ProposalDataManagementForm,
    ProposalStartPracticeForm,
    ProposalSubmitForm,
    RevisionProposalCopyForm,
    AmendmentProposalCopyForm,
    ProposalUpdateDataManagementForm,
    ProposalUpdateDateStartForm,
    ResearcherForm,
    OtherResearchersForm,
    FundingForm,
    ResearchGoalForm,
    PreApprovedForm,
    TranslatedConsentForm,
    ProposalForm,
    KnowledgeSecurityForm,
)
from ..models import Proposal, Wmo
from ..utils import generate_pdf, generate_ref_number
from proposals.mixins import (
    ProposalMixin,
    ProposalContextMixin,
    PDFTemplateResponseMixin,
)
from proposals.utils.proposal_utils import FilenameFactory

############
# List views
############


class BaseProposalsView(LoginRequiredMixin, generic.TemplateView):
    title = _("Publiek archief")
    body = _("Dit overzicht toont alle goedgekeurde aanvragen.")
    is_modifiable = False
    is_submitted = True
    contains_supervised = False
    template_name = "proposals/proposal_list.html"

    def get_context_data(self, **kwargs):
        context = super(BaseProposalsView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["body"] = self.body
        context["modifiable"] = self.is_modifiable
        context["submitted"] = self.is_submitted
        context["supervised"] = self.contains_supervised
        context["data_url"] = None

        return context


class MyProposalsView(BaseProposalsView):
    title = _("Mijn aanvraag")
    body = _("Dit overzicht toont al je aanvragen.")
    is_modifiable = True
    is_submitted = True
    contains_supervised = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse(
            "proposals:api:my_archive",
        )
        return context


class MyConceptsView(BaseProposalsView):
    title = _("Mijn conceptaanvragen")
    body = _("Dit overzicht toont al je nog niet ingediende aanvragen.")
    is_modifiable = True
    is_submitted = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse(
            "proposals:api:my_concepts",
        )
        return context


class MySubmittedView(BaseProposalsView):
    title = _("Mijn ingediende aanvragen")
    body = _("Dit overzicht toont al je ingediende aanvragen.")
    is_modifiable = False
    is_submitted = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse(
            "proposals:api:my_submitted",
        )
        return context


class MyCompletedView(BaseProposalsView):
    title = _("Mijn afgehandelde aanvragen")
    body = _("Dit overzicht toont al je beoordeelde aanvragen.")
    is_modifiable = False
    is_submitted = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse(
            "proposals:api:my_completed",
        )
        return context


class MySupervisedView(BaseProposalsView):
    title = _("Mijn aanvragen als eindverantwoordelijke")
    body = _(
        "Dit overzicht toont alle aanvragen waarvan je eindverantwoordelijke " "bent."
    )
    is_modifiable = True
    is_submitted = True
    contains_supervised = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse(
            "proposals:api:my_supervised",
        )
        return context


class MyPracticeView(BaseProposalsView):
    title = _("Mijn oefenaanvragen")
    body = _(
        "Dit overzicht toont alle oefenaanvragen waar je als student, \
onderzoeker of eindverantwoordelijke bij betrokken bent."
    )
    is_modifiable = True
    is_submitted = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse(
            "proposals:api:my_practice",
        )
        return context


class ProposalUsersOnlyArchiveView(
    HumanitiesOrPrivilegeRequiredMixin, CommitteeMixin, BaseProposalsView
):
    template_name = "proposals/proposal_private_archive.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_url"] = reverse("proposals:api:archive", args=[self.committee])
        return context

    @property
    def title(self):
        return "{} - {}".format(_("Archief"), self.committee_display_name)


class ProposalsPublicArchiveView(generic.ListView):
    template_name = "proposals/proposal_public_archive.html"
    model = Proposal

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon"""
        return Proposal.objects.public_archive()


class ProposalsExportView(GroupRequiredMixin, generic.ListView):
    context_object_name = "proposals"
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]
    template_name_suffix = "_export_list"

    def get_queryset(self):
        """Returns all the Proposals that have been decided positively upon,
        or a single one if specified in the URL"""
        pk = self.kwargs.get("pk")

        if pk is not None:
            return Proposal.objects.filter(pk=pk)

        return Proposal.objects.export()


class ChangeArchiveStatusView(GroupRequiredMixin, generic.RedirectView):
    group_required = settings.GROUP_SECRETARY
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.get("pk")

        proposal = Proposal.objects.get(pk=pk)
        proposal.in_archive = not proposal.in_archive
        proposal.save()
        committee = proposal.reviewing_committee.name
        return reverse("proposals:archive", args=[committee])


##########################
# CRUD actions on Proposal
##########################


class ProposalCreate(AllowErrorsOnBackbuttonMixin, CreateView):
    # Note: template_name is auto-generated to proposal_form.html

    success_message = _("Aanvraag %(title)s aangemaakt")
    template_name = "proposals/proposal_form.html"
    form_class = ProposalForm

    def get_proposal(
        self,
    ):
        return self.get_form().instance

    def form_valid(self, form):
        """
        - Sets created_by to current user
        - Generates a reference number
        - Sets reviewing committee
        - Adds user to applicants
        """
        form.instance.created_by = self.request.user
        form.instance.reference_number = generate_ref_number()
        form.instance.reviewing_committee = form.instance.institution.reviewing_chamber
        obj = form.save()
        obj.applicants.set([self.request.user])
        obj.save()
        return super(ProposalCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Adds 'create'/'no_back' to template context"""
        context = super(ProposalCreate, self).get_context_data(**kwargs)
        context["create"] = True
        context["no_back"] = True
        context["is_practice"] = self.get_proposal().is_practice()
        return context

    def get_next_url(self):
        return reverse("proposals:researcher", args=(self.object.pk,))


class ProposalUpdate(ProposalMixin, AllowErrorsOnBackbuttonMixin, UpdateView):
    form_class = ProposalForm

    def form_valid(self, form):
        """Sets created_by to current user and generates a reference number"""
        form.instance.reviewing_committee = form.instance.institution.reviewing_chamber
        return super(ProposalUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Adds 'create'/'no_back' to template context"""
        context = super(ProposalUpdate, self).get_context_data(**kwargs)
        context["create"] = False
        context["no_back"] = True

        return context

    def get_next_url(self):
        return reverse("proposals:researcher", args=(self.object.pk,))


class ProposalDelete(DeleteView):
    model = Proposal
    success_message = _("Aanvraag verwijderd")

    def get_success_url(self):
        """After deletion, return to the concepts overview"""
        return reverse("proposals:my_concepts")


class CompareDocumentsView(UsersOrGroupsAllowedMixin, generic.TemplateView):
    template_name = "proposals/compare_documents.html"
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    def get_allowed_users(self):
        compare_type = self.kwargs.get("type")
        new_pk = self.kwargs.get("new")
        attribute = self.kwargs.get("attribute")

        model = {
            "documents": Documents,
            "wmo": Wmo,
            "observation": Observation,
            "proposal": Proposal,
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

        context["old_name"] = self.old_file.name
        context["old_file"] = self.old_file
        context["old_text"] = get_document_contents(self.old_file)
        context["new_name"] = self.new_file.name
        context["new_file"] = self.new_file
        context["new_text"] = get_document_contents(self.new_file)

        return context

    def _get_files(self) -> Tuple[Union[None, FieldFile], Union[None, FieldFile]]:
        compare_type = self.kwargs.get("type")
        old_pk = self.kwargs.get("old")
        new_pk = self.kwargs.get("new")
        attribute = self.kwargs.get("attribute")

        model = {
            "documents": Documents,
            "wmo": Wmo,
            "observation": Observation,
            "proposal": Proposal,
        }.get(compare_type, None)

        if model is None:
            return None, None

        old = model.objects.get(pk=old_pk)
        new = model.objects.get(pk=new_pk)

        return getattr(old, attribute, None), getattr(new, attribute, None)


class CompareAttachmentsView(UsersOrGroupsAllowedMixin, generic.TemplateView):

    template_name = "proposals/compare_attachments.html"
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_proposal(
        self,
    ):
        proposal = Proposal.objects.get(
            pk=self.kwargs.get("proposal_pk"),
        )
        return proposal

    def get_allowed_users(
        self,
    ):
        self._get_attachments()
        proposal = self.get_proposal()
        allowed_users = set()

        # Users allowed to compare these files must be allowed to see both
        # attachments individually.
        def allowed_for_attachment(proposal, attachment):
            allowed = set()
            allowed.add(attachment.author)
            allowed.add(proposal.applicants.all())
            return allowed

        intersection = allowed_for_attachment(
            proposal, self.new
        ) & allowed_for_attachment(proposal.parent, self.old)
        allowed_users = allowed_users | intersection
        # The current supervisor gets a pass. If they try to access files
        # other than those in the parent proposal get_attachments should raise
        # a PermissionDenied.
        allowed_users.add(proposal.supervisor)
        return allowed_users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proposal"] = self.get_proposal()
        context["old_name"] = self.old.upload.original_filename
        context["old_file"] = self.old.upload
        context["old_attachment"] = self.old
        context["old_text"] = get_document_contents(self.old.upload)
        context["new_name"] = self.new.upload.original_filename
        context["new_file"] = self.new.upload
        context["new_attachment"] = self.new
        context["new_text"] = get_document_contents(self.new.upload)
        return context

    def _get_attachments(
        self,
    ):
        # Fetch relevant objects
        self.old = Attachment.objects.get(
            pk=self.kwargs.get("old_pk"),
        ).get_correct_submodel()

        self.new = Attachment.objects.get(
            pk=self.kwargs.get("new_pk"),
        ).get_correct_submodel()

        self.proposal = Proposal.objects.get(
            pk=self.kwargs.get("proposal_pk"),
        )
        # Check the old attachment is within scope
        if type(self.old) is StudyAttachment:
            old_proposals = [ao.proposal for ao in self.old.attached_to.all()]
        else:
            old_proposals = self.old.attached_to.all()
        if self.proposal.parent not in old_proposals:
            raise PermissionDenied("Couldn't find old_pk in proposal's ancestors!")


###########################
# Other actions on Proposal
###########################
class ProposalStart(generic.TemplateView):
    template_name = "proposals/proposal_start.html"

    def get_context_data(self, **kwargs):
        """Adds secretary and link to regulations to template context"""
        context = super(ProposalStart, self).get_context_data(**kwargs)
        context["secretary"] = get_secretary()
        return context


class ProposalResearcherFormView(
    ProposalMixin,
    UserFormKwargsMixin,
    ProposalContextMixin,
    AllowErrorsOnBackbuttonMixin,
    UpdateView,
):
    model = Proposal
    form_class = ResearcherForm
    template_name = "proposals/researcher_form.html"

    def get_next_url(self):
        return reverse("proposals:other_researchers", args=(self.object.pk,))

    def get_back_url(self):
        return reverse("proposals:update", args=(self.object.pk,))


class ProposalOtherResearchersFormView(
    UserFormKwargsMixin,
    AllowErrorsOnBackbuttonMixin,
    ProposalMixin,
    UpdateView,
):
    model = Proposal
    form_class = OtherResearchersForm
    template_name = "proposals/other_researchers_form.html"

    def form_valid(self, form):
        """
        Ensure:
        - if other_applicants is False, only the user is in applicants
        - if other_applicants is True, always add current user to applicants
        """
        response = super(ProposalOtherResearchersFormView, self).form_valid(form)
        self.object = form.save()
        if form.instance.other_applicants == False:
            self.object.applicants.set([self.request.user])
        else:
            self.object.applicants.add(self.request.user)
        return response

    def get_next_url(self):
        proposal = self.object
        return reverse("proposals:funding", args=(self.object.pk,))

    def get_back_url(self):
        return reverse("proposals:researcher", args=(self.object.pk,))


class ProposalFundingFormView(
    ProposalContextMixin, AllowErrorsOnBackbuttonMixin, UpdateView
):
    model = Proposal
    form_class = FundingForm
    template_name = "proposals/funding_form.html"

    def get_next_url(self):
        return reverse("proposals:research_goal", args=(self.object.pk,))

    def get_back_url(self):
        return reverse("proposals:other_researchers", args=(self.object.pk,))


class ProposalResearchGoalFormView(
    ProposalContextMixin, AllowErrorsOnBackbuttonMixin, UpdateView
):
    model = Proposal
    form_class = ResearchGoalForm
    template_name = "proposals/research_goal_form.html"

    def get_next_url(self):
        proposal = self.object
        if proposal.is_pre_assessment:
            pre_suffix = "_pre"
        else:
            pre_suffix = ""
        if proposal.is_pre_approved:
            return reverse("proposals:pre_approved", args=(self.object.pk,))
        elif hasattr(proposal, "wmo"):
            return reverse(f"proposals:wmo_update{pre_suffix}", args=(proposal.wmo.pk,))
        else:
            return reverse(f"proposals:wmo_create{pre_suffix}", args=(proposal.pk,))

    def get_back_url(self):
        proposal = self.object
        if proposal.is_pre_assessment:
            return reverse("proposals:other_researchers", args=(self.object.pk,))
        else:
            return reverse("proposals:funding", args=(self.object.pk,))


class ProposalPreApprovedFormView(
    ProposalContextMixin, AllowErrorsOnBackbuttonMixin, UpdateView
):
    model = Proposal
    form_class = PreApprovedForm
    template_name = "proposals/pre_approved_form.html"

    def get_next_url(self):
        """Go to the Other Researcher page"""

        return reverse("proposals:submit_pre_approved", args=(self.object.pk,))

    def get_back_url(self):
        """Return to the Proposal Form page"""
        return reverse("proposals:research_goal", args=(self.object.pk,))


class ProposalKnowledgeSecurity(
    ProposalContextMixin, AllowErrorsOnBackbuttonMixin, UpdateView
):
    model = Proposal
    form_class = KnowledgeSecurityForm
    template_name = "proposals/knowledge_security_form.html"

    def get_next_url(self):
        return reverse("proposals:data_management", args=(self.object.pk,))

    def get_back_url(self):
        return reverse("studies:design_end", args=(self.object.last_study().pk,))


class TranslatedConsentView(ProposalContextMixin, UpdateView):
    model = Proposal
    form_class = TranslatedConsentForm
    template_name = "proposals/translated_consent_forms.html"

    def get_next_url(self):
        """Go to the consent form upload page"""
        return reverse("proposals:submit", args=(self.object.pk,))

    def get_back_url(self):
        """Return to the overview of the last Study"""
        return reverse("proposals:attachments", args=(self.object.pk,))


class ProposalDataManagement(ProposalContextMixin, UpdateView):
    model = Proposal
    form_class = ProposalDataManagementForm
    template_name = "proposals/proposal_data_management.html"

    def get_next_url(self):
        """Continue to the submission view"""
        return reverse("proposals:attachments", args=(self.object.pk,))

    def get_back_url(self):
        """Return to the consent form overview of the last Study"""
        return reverse("proposals:knowledge_security", args=(self.object.pk,))


class ProposalUpdateDataManagement(GroupRequiredMixin, generic.UpdateView):
    """
    Allows the secretary to change the Data Management Plan on the Proposal level
    """

    model = Proposal
    template_name = "proposals/proposal_update_dmp.html"
    form_class = ProposalUpdateDataManagementForm
    group_required = settings.GROUP_SECRETARY

    def form_valid(self, form):
        ret = super().form_valid(form)
        # Always regenerate the PDF after updating the DMP
        # This is necessary, as the canonical PDF protection might already
        # have kicked in if the secretary changes the documents later than
        # we initially expected.
        self.object.generate_pdf(force_overwrite=True)

        return ret

    def get_success_url(self):
        """Continue to the URL specified in the 'next' POST parameter"""
        return reverse("reviews:detail", args=[self.object.latest_review().pk])

    def get_back_url(
        self,
    ):
        if self.get_proposal().is_pre_approved:
            return reverse(
                "proposals:pre_approved",
                args=[self.get_proposal().pk],
            )
        return reverse(
            "proposals:knowledge_security",
            args=[self.get_proposal().pk],
        )


class ProposalUpdateDateStart(GroupRequiredMixin, generic.UpdateView):
    """
    Allows the secretary to change the date_start on the Proposal level
    """

    model = Proposal
    template_name = "proposals/proposal_update_date_start.html"
    form_class = ProposalUpdateDateStartForm
    group_required = settings.GROUP_SECRETARY

    def form_valid(self, form):
        ret = super().form_valid(form)
        # Always regenerate the PDF after updating the DMP
        # This is necessary, as the canonical PDF protection might already
        # have kicked in if the secretary changes the documents later than
        # we initially expected.
        self.object.generate_pdf(force_overwrite=True)

        return ret

    def get_success_url(self):
        """Continue to the URL specified in the 'next' POST parameter"""
        return reverse("reviews:detail", args=[self.object.latest_review().pk])


class ProposalSubmit(
    ProposalContextMixin,
    AllowErrorsOnBackbuttonMixin,
    UpdateView,
):
    model = Proposal
    form_class = ProposalSubmitForm
    template_name = "proposals/proposal_submit.html"
    success_message = _("Wijzigingen opgeslagen")

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(ProposalSubmit, self).get_form_kwargs()
        kwargs["proposal"] = self.get_object()

        # Required for examining POST data
        # to check for js-redirect-submit
        kwargs["request"] = self.request

        # The following is a flag to let form validation know that
        # this is an actual user attempting to submit the form, and not
        # background validation by the Stepper.
        kwargs["final_validation"] = True

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProposalSubmit, self).get_context_data(**kwargs)

        context["pagenr"] = self._get_page_number()
        context["is_supervisor_edit_phase"] = self.is_supervisor_edit_phase()
        context["start_date_warning"] = self.check_start_date()

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
        if self.object.status == self.object.Statuses.SUBMITTED_TO_SUPERVISOR:
            return True
        return False

    def form_valid(self, form):
        """
        Start a review for this proposal and return a response.
        """
        # We pick up the response from the base class first so that
        # the fields on the Submit page get saved correctly. In the end,
        # this is still an UpdateView
        success_response = super().form_valid(form)
        # We then defer all submission logic to the utility code.
        # Checks for practice proposals and starting the right
        # kind of review happen over there.
        proposal = form.instance
        if (
            "save_back" not in self.request.POST
            and "js-redirect-submit" not in self.request.POST
        ):
            start_review(proposal)
        return success_response

    def get_next_url(self):
        """After submission, go to the thank-you view. Unless a supervisor is
        editing the proposal during their review, in that case: go to their
        decide page"""
        if self.is_supervisor_edit_phase() and self.current_user_is_supervisor():
            review = self.object.latest_review()
            decision = review.decision_set.get(reviewer=self.request.user)
            return reverse("reviews:decide", args=(decision.pk,))

        return reverse("proposals:submitted", args=(self.object.pk,))

    def get_back_url(self):
        """Return to the data management view"""
        return reverse("proposals:translated", args=(self.object.pk,))

    def _get_page_number(self):
        if self.object.is_pre_assessment:
            return 3

        if self.object.is_pre_approved:
            return 2

        return 6


class ProposalSubmitted(generic.DetailView):
    model = Proposal
    template_name = "proposals/proposal_submitted.html"


class ProposalConfirmation(GroupRequiredMixin, generic.UpdateView):
    model = Proposal
    template_name = "proposals/proposal_confirmation.html"
    form_class = ProposalConfirmationForm
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        """On confirmation, return to the Review archive"""
        committee = self.object.reviewing_committee.name
        return reverse("reviews:my_archive", args=[committee])


class ProposalCopy(UserFormKwargsMixin, CreateView):
    model = Proposal
    form_class = ProposalCopyForm
    success_message = _("Aanvraag gekopieerd")
    template_name = "proposals/proposal_copy.html"

    def get_initial(self):
        """Sets initial value of is_revision to False. It's a hidden field,
        so this value will also be the actual value. Used for the different
        behaviour for this class' subclasses
        """
        initial = super(ProposalCopy, self).get_initial()
        initial["is_revision"] = False
        return initial

    def form_valid(self, form):
        """Create a copy of the selected Proposal"""
        form.instance = copy_proposal(
            form.cleaned_data["parent"],
            form.cleaned_data["is_revision"],
            self.request.user,
        )
        return super(ProposalCopy, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_revision"] = False
        context["is_amendment"] = False

        return context


class ProposalCopyRevision(ProposalCopy):
    form_class = RevisionProposalCopyForm

    def get_initial(self):
        """Sets initial value of is_revision to True"""
        initial = super(ProposalCopyRevision, self).get_initial()
        initial["is_revision"] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_revision"] = True

        return context


class ProposalCopyAmendment(ProposalCopy):
    form_class = AmendmentProposalCopyForm

    def get_initial(self):
        """Sets initial value of is_revision to True"""
        initial = super(ProposalCopyAmendment, self).get_initial()
        initial["is_revision"] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_amendment"] = True

        return context


class ProposalAsPdf(
    LoginRequiredMixin,
    generic.DetailView,
    PDFTemplateResponseMixin,
):
    model = Proposal
    # The PDF mixin generates a filename with this factory
    filename_factory = FilenameFactory("Proposal")
    template_name = "proposals/proposal_pdf.html"

    def get(self, request, *args, **kwargs):
        # First, check if we should use a pregenerated pdf, if we have one
        proposal = self.get_object()
        if proposal.use_canonical_pdf():
            if proposal.pdf:
                return FileResponse(
                    proposal.pdf,
                    filename=self.get_pdf_filename(),
                    as_attachment=self.pdf_save_as,
                )
        # Else, continue with generation
        return super().get(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        """If we already have an object set, use that.
        This can happen if this view is being called from generate_pdf()
        rather than by Django."""
        if not hasattr(self, "object"):
            self.object = super().get_object(*args, **kwargs)
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = create_context_pdf(context, self.object)

        return context


class ProposalDifference(LoginRequiredMixin, generic.DetailView):
    model = Proposal
    template_name = "proposals/proposal_diff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = create_context_diff(context, self.object.parent, self.object)

        return context


########################
# Preliminary assessment
########################
class ProposalStartPreAssessment(ProposalStart):
    template_name = "proposals/proposal_start_pre_assessment.html"


class ProposalCreatePreAssessment(ProposalCreate):
    def form_valid(self, form):
        """Sets is_pre_assessment to True"""
        form.instance.is_pre_assessment = True
        return super(ProposalCreatePreAssessment, self).form_valid(form)


class ProposalSubmitPreAssessment(ProposalSubmit):
    def get_next_url(self):
        """After submission, go to the thank-you view"""
        return reverse("proposals:submitted_pre", args=(self.object.pk,))

    def get_back_url(self):
        """Return to the Wmo overview"""
        return reverse("proposals:attachments", args=(self.object.pk,))


class ProposalSubmittedPreAssessment(ProposalSubmitted):
    template_name = "proposals/proposal_submitted.html"


#############
# Pre-Aproved
#############


class ProposalStartPreApproved(ProposalStart):
    template_name = "proposals/proposal_start_pre_approved.html"


class ProposalCreatePreApproved(ProposalCreate):

    def form_valid(self, form):
        """Sets is_pre_approved to True"""
        form.instance.is_pre_approved = True
        return super(ProposalCreatePreApproved, self).form_valid(form)


class ProposalSubmitPreApproved(ProposalSubmit):
    def get_next_url(self):
        """After submission, go to the thank-you view"""
        return reverse("proposals:submitted_pre_approved", args=(self.object.pk,))


class ProposalSubmittedPreApproved(ProposalSubmitted):
    template_name = "proposals/proposal_submitted.html"


##########
# Practice
##########
class ProposalStartPractice(generic.FormView):
    template_name = "proposals/proposal_start_practice.html"
    form_class = ProposalStartPracticeForm

    def get_context_data(self, **kwargs):
        """Adds 'secretary', 'is_practice' and 'no_back' to template context"""
        context = super(ProposalStartPractice, self).get_context_data(**kwargs)
        context["secretary"] = get_secretary()
        context["is_practice"] = True
        context["no_back"] = True
        return context

    def get_success_url(self):
        """Go to the creation for a practice Proposal"""
        return reverse(
            "proposals:create_practice", args=(self.request.POST["practice_reason"],)
        )


class ProposalCreatePractice(ProposalCreate):
    def get_context_data(self, **kwargs):
        """Adds 'is_practice' to template context"""
        context = super(ProposalCreatePractice, self).get_context_data(**kwargs)
        context["is_practice"] = True
        return context

    def form_valid(self, form):
        """Sets in_course and is_exploration"""
        form.instance.in_course = (
            self.kwargs["reason"] == Proposal.PracticeReasons.COURSE
        )
        form.instance.is_exploration = (
            self.kwargs["reason"] == Proposal.PracticeReasons.EXPLORATION
        )
        return super(ProposalCreatePractice, self).form_valid(form)
