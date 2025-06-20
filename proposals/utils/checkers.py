from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from proposals import forms as proposal_forms
from proposals.models import Wmo
from proposals.mixins import SupervisorEditingMixin
from studies import forms as study_forms
from studies.models import Study
from interventions import forms as intervention_forms
from observations import forms as observation_forms
from tasks import forms as tasks_forms

from tasks.views import task_views, session_views
from tasks.models import Task, Session

from attachments.utils import AttachmentSlot, desiredness, OptionalityGroup
from attachments.kinds import (
    DataManagementPlan,
    LEGAL_BASIS_KIND_DICT,
    ConsentFormAdults,
    AgreementRecordingsAdults,
    AgreementRecordingsChildrenNoParents,
    AgreementRecordingsChildrenParents,
    ScriptVerbalConsentRecordings,
    ConsentPublicInterestSpecialDetails,
    ConsentChildrenParents,
    ConsentChildrenNoParents,
    SchoolConsentForm,
    SchoolInformationLetter,
)

from .stepper_helpers import (
    Checker,
    PlaceholderItem,
    StepperItem,
    ContainerItem,
    ModelFormChecker,
    ModelFormItem,
    UpdateOrCreateChecker,
)


class ProposalTypeChecker(
    Checker,
):

    def check(self):
        """Each proposal type receives a specific create checker and layout"""
        from .stepper import (
            RegularProposalLayout,
            PreApprProposalLayout,
            PreAssProposalLayout,
        )

        if self.proposal.is_pre_approved:
            self.stepper.layout = PreApprProposalLayout
        elif self.proposal.is_pre_assessment:
            self.stepper.layout = PreAssProposalLayout
        else:
            self.stepper.layout = RegularProposalLayout
        return [ProposalCreateChecker]


class ProposalCreateChecker(
    ModelFormChecker,
):
    title = _("Basisgegevens")
    location = "create"
    form_class = proposal_forms.ProposalForm

    def get_url(self):
        return reverse(
            "proposals:update",
            args=[self.proposal.pk],
        )

    def check(self):
        self.item = ModelFormItem(
            self.stepper,
            title=self.title,
            form_object=self.proposal,
            form_class=self.form_class,
            form_kwargs={},
            url_func=self.get_url,
            location=self.location,
        )
        self.stepper.items.append(
            self.item,
        )
        return [
            ResearcherChecker(
                self.stepper,
                parent=self.item,
            )
        ]


class ResearcherChecker(
    SupervisorEditingMixin,
    ModelFormChecker,
):
    title = _("Onderzoeker")
    form_class = proposal_forms.ResearcherForm

    def check(self):
        self.stepper.items.append(self.make_stepper_item())
        return [OtherResearchersChecker(self.stepper, parent=self.parent)]

    def get_url(self):
        return reverse(
            "proposals:researcher",
            args=(self.proposal.pk,),
        )


class OtherResearchersChecker(
    ModelFormChecker,
):
    title = _("Andere onderzoekers")
    form_class = proposal_forms.OtherResearchersForm

    def check(self):
        self.stepper.items.append(self.make_stepper_item())
        return [
            FundingChecker(
                self.stepper,
                parent=self.parent,
            )
        ]

    def get_url(self):
        return reverse(
            "proposals:other_researchers",
            args=(self.proposal.pk,),
        )


class FundingChecker(
    ModelFormChecker,
):
    title = _("Financiering")
    form_class = proposal_forms.FundingForm

    def check(self):
        self.stepper.items.append(self.make_stepper_item())
        return [
            GoalChecker(
                self.stepper,
                parent=self.parent,
            )
        ]

    def get_url(self):
        return reverse(
            "proposals:funding",
            args=(self.proposal.pk,),
        )


class GoalChecker(
    ModelFormChecker,
):
    title = _("Onderzoeksdoel")
    form_class = proposal_forms.ResearchGoalForm

    def check(self):
        self.stepper.items.append(self.make_stepper_item())
        return [
            PreApprovedChecker(
                self.stepper,
                parent=self.parent,
            )
        ]

    def get_url(self):
        return reverse(
            "proposals:research_goal",
            args=(self.proposal.pk,),
        )


class PreApprovedChecker(
    ModelFormChecker,
):

    title = _("Eerdere toetsing")
    form_class = proposal_forms.PreApprovedForm

    def check(self):
        if self.proposal.is_pre_approved:
            self.stepper.items.append(self.make_stepper_item())
        return [WMOChecker]

    def get_url(self):
        return reverse(
            "proposals:pre_approved",
            args=(self.proposal.pk,),
        )


class WMOChecker(ModelFormChecker):

    title = "WMO"
    form_class = proposal_forms.WmoForm
    location = "wmo"

    def check(
        self,
    ):
        if self.proposal.is_pre_approved:
            return [TrajectoriesChecker]
        self.item = self.make_stepper_item()
        self.stepper.items.append(
            self.item,
        )
        if self.object_exists():
            return self.check_wmo()
        else:

            def no_wmo_error():
                return [_("WMO gegevens ontbreken")]

            self.item.get_checker_errors = no_wmo_error
            return []

    def check_wmo(
        self,
    ):
        """
        This method should check the correctness of the
        WMO object.
        """
        if self.proposal.wmo.status != Wmo.WMOStatuses.NO_WMO:
            return [
                WMOApplicationChecker(
                    self.stepper,
                    parent=self.item,
                )
            ]
        return [TrajectoriesChecker]

    def get_url(self):
        if self.object_exists():
            return self.get_update_url()
        else:
            return self.get_create_url()

    def object_exists(
        self,
    ):
        return hasattr(
            self.proposal,
            "wmo",
        )

    def get_create_url(
        self,
    ):
        if self.proposal.is_pre_assessment:
            url = "proposals:wmo_create_pre"
        else:
            url = "proposals:wmo_create"
        return reverse(
            url,
            args=[self.proposal.pk],
        )

    def get_update_url(
        self,
    ):
        if self.proposal.is_pre_assessment:
            url = "proposals:wmo_update_pre"
        else:
            url = "proposals:wmo_update"
        return reverse(
            url,
            args=[self.proposal.wmo.pk],
        )

    def get_form_object(
        self,
    ):
        if self.object_exists():
            return self.proposal.wmo
        else:
            return None


class WMOApplicationChecker(ModelFormChecker):

    title = _("WMO applicatie")
    form_class = proposal_forms.WmoApplicationForm

    def check(self):
        self.stepper.items.append(self.make_stepper_item())
        if self.proposal.wmo.status == Wmo.WMOStatuses.WAITING:
            return []
        return [TrajectoriesChecker]

    def get_url(self):
        if self.proposal.is_pre_assessment:
            pre_suffix = "_pre"
        else:
            pre_suffix = ""
        return reverse(
            f"proposals:wmo_application{pre_suffix}",
            args=(self.proposal.wmo.pk,),
        )

    def get_form_object(self):
        return self.proposal.wmo


class TrajectoriesChecker(
    ModelFormChecker,
):
    form_class = proposal_forms.StudyStartForm
    title = _("Trajecten")
    location = "studies"

    def check(
        self,
    ):
        proposal = self.proposal
        if proposal.is_pre_assessment or proposal.is_pre_approved:
            return self.remaining_checkers()
        self.item = self.make_stepper_item()
        self.stepper.items.append(self.item)
        sub_items = [self.make_study_checker(s) for s in self.get_studies()]
        ksc = KnowledgeSecurityChecker(self.stepper, parent=self.item)
        return sub_items + [ksc] + self.remaining_checkers()

    def make_study_checker(self, study):
        return StudyChecker(
            self.stepper,
            parent=self.item,
            study=study,
        )

    def remaining_checkers(
        self,
    ):
        return [
            DataManagementChecker,
            AttachmentsChecker,
            SubmitChecker,
        ]

    def get_studies(
        self,
    ):
        proposal = self.stepper.proposal
        return list(
            proposal.study_set.all(),
        )

    def get_url(
        self,
    ):
        return reverse(
            "proposals:study_start",
            args=[self.proposal.pk],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["proposal"] = self.proposal
        return kwargs


class KnowledgeSecurityChecker(
    ModelFormChecker,
):
    form_class = proposal_forms.KnowledgeSecurityForm
    title = _("Traject afronding")

    def check(self):
        if self.stepper.has_multiple_studies():
            self.title = _("Trajecten afronding")
        self.stepper.items.append(self.make_stepper_item())
        return []

    def get_url(
        self,
    ):
        return reverse("proposals:knowledge_security", args=[self.proposal.pk])


class StudyChecker(
    Checker,
):
    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(
        self,
    ):
        self.current_parent = self.parent
        checkers = []
        if self.stepper.has_multiple_studies():
            # Create an intermediate container item per study,
            # if we have more than one
            self.current_parent = ContainerItem(
                stepper=self.stepper,
                title=self.study.name,
                parent=self.parent,
            )
            self.stepper.items.append(self.current_parent)
        # We always have a Participants and StudyDesign item
        checkers = [
            ParticipantsChecker(
                self.stepper,
                study=self.study,
                parent=self.current_parent,
            ),
            PersonalDataChecker(
                self.stepper,
                study=self.study,
                parent=self.current_parent,
            ),
            RegistrationChecker(
                self.stepper,
                study=self.study,
                parent=self.current_parent,
            ),
            DesignChecker(
                self.stepper,
                study=self.study,
                parent=self.current_parent,
            ),
        ]
        final_checkers = [
            StudyEndChecker(
                self.stepper,
                study=self.study,
                parent=self.current_parent,
            ),
            StudyAttachmentsChecker(
                self.stepper,
                study=self.study,
            ),
        ]
        return checkers + self.determine_study_checkers(self.study) + final_checkers

    def determine_study_checkers(self, study):
        tests = {
            self.make_intervention: lambda s: s.has_intervention,
            self.make_observation: lambda s: s.has_observation,
            self.make_sessions: lambda s: s.has_sessions,
        }
        optional_checkers = [
            maker(study) for maker, test in tests.items() if test(study)
        ]
        return optional_checkers

    def make_intervention(self, study):
        return InterventionChecker(
            self.stepper,
            study=study,
            parent=self.current_parent,
        )

    def make_observation(self, study):
        return ObservationChecker(
            self.stepper,
            study=study,
            parent=self.current_parent,
        )

    def make_sessions(self, study):
        return SessionsChecker(
            self.stepper,
            study=study,
            parent=self.current_parent,
        )


class StudyAttachmentsChecker(
    Checker,
):

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.study = kwargs.pop("study")
        super().__init__(*args, **kwargs)

    def check(
        self,
    ):

        # INFORMATION LETTER LOGIC

        if self.study.legal_basis is not None:
            kind = LEGAL_BASIS_KIND_DICT[self.study.legal_basis]
            info_slot = AttachmentSlot(
                self.study,
                kind=kind,
            )
            self.stepper.add_slot(info_slot)

        # LOGIC FOR PUBLIC INTEREST

        if self.study.legal_basis == Study.LegalBases.PUBLIC_INTEREST:

            if self.study.has_recordings():
                if self.study.has_adults():
                    # if a study features registration, add two slots
                    recording_adults_group = OptionalityGroup()
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=ScriptVerbalConsentRecordings,
                            optionality_group=recording_adults_group,
                        ),
                    )
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=AgreementRecordingsAdults,
                            optionality_group=recording_adults_group,
                        ),
                    )

                if self.study.has_children():
                    # if a study features registration of minors, add two slots
                    recording_minors_group = OptionalityGroup()
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=AgreementRecordingsChildrenNoParents,
                            optionality_group=recording_minors_group,
                        ),
                    )
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=AgreementRecordingsChildrenParents,
                            optionality_group=recording_minors_group,
                        ),
                    )

            elif self.study.has_special_details:
                self.stepper.add_slot(
                    AttachmentSlot(
                        self.study,
                        kind=ConsentPublicInterestSpecialDetails,
                    )
                )

        # LOGIC FOR CONSENT

        if self.study.legal_basis == Study.LegalBases.CONSENT:

            # if there are adults, make the adult consent form required or
            # if there are recordings, either the adult consent form or Script
            if self.study.has_adults():

                if self.study.has_recordings():
                    recording_adults_consent_group = OptionalityGroup()
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=ConsentFormAdults,
                            optionality_group=recording_adults_consent_group,
                        ),
                    )
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=ScriptVerbalConsentRecordings,
                            optionality_group=recording_adults_consent_group,
                        ),
                    )
                else:
                    self.stepper.add_slot(
                        AttachmentSlot(
                            self.study,
                            kind=ConsentFormAdults,
                        )
                    )

            if self.study.has_children():
                child_group = OptionalityGroup()
                self.stepper.add_slot(
                    AttachmentSlot(
                        self.study,
                        kind=ConsentChildrenParents,
                        optionality_group=child_group,
                    ),
                )
                self.stepper.add_slot(
                    AttachmentSlot(
                        self.study,
                        kind=ConsentChildrenNoParents,
                        optionality_group=child_group,
                    ),
                )

        return []


class BaseStudyFormChecker(
    ModelFormChecker,
):
    """
    A base checker class for some of the forms handling Studies
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(
        self,
    ):
        self.stepper.items.append(self.make_stepper_item())
        return []

    def get_form_object(self):
        return self.study


class ParticipantsChecker(
    BaseStudyFormChecker,
):
    title = _("Deelnemers")
    form_class = study_forms.StudyForm

    def get_url(
        self,
    ):
        return reverse(
            "studies:update",
            args=[
                self.study.pk,
            ],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["proposal"] = self.proposal
        return kwargs


class PersonalDataChecker(BaseStudyFormChecker):
    title = _("Persoonsgegevens")
    form_class = study_forms.PersonalDataForm

    def get_url(
        self,
    ):
        return reverse(
            "studies:personal_data",
            args=[
                self.study.pk,
            ],
        )


class RegistrationChecker(
    BaseStudyFormChecker,
):
    title = _("Registratie")
    form_class = study_forms.RegistrationForm

    def get_url(
        self,
    ):
        return reverse(
            "studies:registration",
            args=[
                self.study.pk,
            ],
        )


class DesignChecker(
    BaseStudyFormChecker,
):
    title = _("Ontwerp")
    form_class = study_forms.StudyDesignForm

    def get_url(
        self,
    ):
        return reverse(
            "studies:design",
            args=[
                self.study.pk,
            ],
        )


class StudyEndChecker(
    BaseStudyFormChecker,
):
    title = _("Traject overzicht")
    form_class = study_forms.StudyEndForm

    def get_url(
        self,
    ):
        return reverse(
            "studies:design_end",
            args=[
                self.study.pk,
            ],
        )


class InterventionChecker(
    UpdateOrCreateChecker,
):
    form_class = intervention_forms.InterventionForm
    title = _("Interventie")

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(
        self,
    ):
        self.stepper.items.append(
            self.make_stepper_item(),
        )
        return []

    def object_exists(
        self,
    ):
        return hasattr(
            self.study,
            "intervention",
        )

    def get_form_object(
        self,
    ):
        return self.study.intervention

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["study"] = self.study
        return kwargs

    def get_create_url(
        self,
    ):
        return reverse(
            "interventions:create",
            args=[self.study.pk],
        )

    def get_update_url(
        self,
    ):
        return reverse(
            "interventions:update",
            args=[self.study.intervention.pk],
        )


class ObservationChecker(
    UpdateOrCreateChecker,
):

    form_class = observation_forms.ObservationForm
    title = _("Observatie")

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(
        self,
    ):
        self.stepper.items.append(
            self.make_stepper_item(),
        )
        return []

    def object_exists(
        self,
    ):
        return hasattr(
            self.study,
            "observation",
        )

    def get_create_url(
        self,
    ):
        return reverse(
            "observations:create",
            args=[self.study.pk],
        )

    def get_update_url(
        self,
    ):
        return reverse(
            "observations:update",
            args=[self.study.observation.pk],
        )

    def get_form_object(
        self,
    ):
        return self.study.observation

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["study"] = self.study
        return kwargs


class SessionsChecker(
    ModelFormChecker,
):

    form_class = tasks_forms.SessionOverviewForm
    title = _("Sessies")

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(
        self,
    ):
        self.stepper.items.append(
            self.make_stepper_item(),
        )
        return []

    def make_stepper_item(
        self,
    ):
        """
        An absolutely ridiculous piece of work just to have the right
        stepper item be bold for all underlying task/session views.
        Don't ask me how much time I spent on this.
        """
        item = ModelFormItem(
            self.stepper,
            title=self.title,
            parent=self.parent,
            form_object=self.get_form_object(),
            form_class=self.form_class,
            form_kwargs=self.get_form_kwargs(),
            url_func=self.get_url,
            error_func=self.get_checker_errors,
        )

        def modified_is_current(self, request):
            if request.path_info == self.get_url():
                return True
            # Strip beginning of request path
            subpath = request.path_info.replace(
                "/tasks/",
                "",
                1,
            )

            # Define function to match PK
            def pk_matches_study(view, given_pk, study):
                # These views have a Study object
                if view in [
                    session_views.SessionCreate,
                    session_views.SessionOverview,
                ]:
                    return given_pk == study.pk
                # These have a Task object
                if view in [
                    task_views.TaskUpdate,
                    task_views.TaskDelete,
                ]:
                    return Task.objects.filter(
                        pk=given_pk,
                        session__in=study.session_set.all(),
                    ).exists()
                # Everything else has a Session object
                else:
                    return Session.objects.filter(
                        pk=given_pk,
                        study__pk=study.pk,
                    ).exists()

            # Check tasks URL patterns
            from tasks.urls import urlpatterns

            for pat in urlpatterns:
                # If any of them match, check the PK
                if match := pat.resolve(subpath):
                    view = match.func.view_class
                    pk = match.kwargs["pk"]
                    return pk_matches_study(view, pk, self.study)
            # If all else fails, guess we're not current
            return False

        # Overwrite method at the instance level
        # Strategy taken from types.MethodType and copied verbatim
        # here for clarity
        class _C:  # NoQA
            def _m(
                self,
            ):
                pass

        MethodType = type(_C()._m)
        # The type of _m is a method, bound to class instance _C, and
        # MethodType is its constructor. MethodType takes a function
        # and a class instance and returns a method bound to that instance,
        # allowing for self-reference as expected.
        item.is_current = MethodType(modified_is_current, item)
        # Provide study to the modified is_current
        item.study = self.study
        return item

    def get_form_object(
        self,
    ):
        return self.study

    def get_url(
        self,
    ):
        return reverse(
            "tasks:session_overview",
            args=[self.study.pk],
        )

    def get_checker_errors(self):
        from proposals.utils.validate_sessions_tasks import validate_sessions_tasks

        if validate_sessions_tasks(self.study, self.stepper.has_multiple_studies()):
            return ["sub_page_errors"]
        return []


class AttachmentsItem(
    StepperItem,
):
    title = _("Documenten")
    location = "attachments"

    def get_url(
        self,
    ):
        url = reverse(
            "proposals:attachments",
            args=[self.stepper.proposal.pk],
        )
        return url

    def get_errors(self, include_children=False):
        errors = super().get_errors(include_children=include_children)
        for slot in self.stepper.attachment_slots:
            if not slot.attachment:
                if slot.required:
                    errors.append(
                        slot.kind.name,
                    )
        return errors


class DataManagementChecker(
    ModelFormChecker,
):
    title = _("Data management")
    form_class = proposal_forms.ProposalDataManagementForm
    location = "data_management"

    def check(
        self,
    ):
        if self.proposal.is_pre_assessment:
            return []
        self.stepper.items.append(
            self.make_stepper_item(),
        )
        return []

    def get_url(
        self,
    ):
        return reverse(
            "proposals:data_management",
            args=[
                self.stepper.proposal.pk,
            ],
        )


class AttachmentsChecker(
    Checker,
):
    def check(
        self,
    ):
        self.add_dmp_slot()
        self.add_school_slots()
        item = self.make_stepper_item()
        self.stepper.items.append(item)
        return [
            TranslationChecker(
                self.stepper,
                parent=item,
            ),
        ]

    def add_dmp_slot(self):
        if self.proposal.is_pre_assessment:
            return
        slot = AttachmentSlot(
            self.stepper.proposal,
            kind=DataManagementPlan,
        )
        self.stepper.add_slot(slot)

    def add_school_slots(self):
        result_des = False
        for study in self.proposal.study_set.all():
            # Get highest desiredness of all studies
            study_gd = study.get_gatekeeper_desiredness()
            if study_gd is desiredness.REQUIRED:
                result_des = desiredness.REQUIRED
                break
            if study_gd is desiredness.OPTIONAL:
                result_des = desiredness.OPTIONAL
        if result_des:
            self.stepper.add_slot(
                AttachmentSlot(
                    self.stepper.proposal,
                    kind=SchoolInformationLetter,
                    force_desiredness=result_des,
                )
            )
            self.stepper.add_slot(
                AttachmentSlot(
                    self.stepper.proposal,
                    kind=SchoolConsentForm,
                    force_desiredness=result_des,
                )
            )

    def make_stepper_item(self):
        item = AttachmentsItem(
            self.stepper,
        )
        return item


class TranslationChecker(
    ModelFormChecker,
):
    form_class = proposal_forms.TranslatedConsentForm
    title = _("Vertalingen")
    location = "data_management"

    def check(
        self,
    ):
        if not self.proposal.is_pre_assessment:
            self.stepper.items.append(self.make_stepper_item())
        return []

    def get_url(
        self,
    ):
        return reverse(
            "proposals:translated",
            args=[
                self.stepper.proposal.pk,
            ],
        )


class SubmitChecker(
    ModelFormChecker,
):
    title = _("Indienen")
    form_class = proposal_forms.ProposalSubmitForm
    location = "submit"

    def check(
        self,
    ):
        self.stepper.items.append(
            self.make_stepper_item(),
        )
        return []

    def get_url(
        self,
    ):
        url_string = "proposals:submit"
        if self.proposal.is_pre_assessment:
            url_string = "proposals:submit_pre"
        if self.proposal.is_pre_approved:
            url_string = "proposals:submit_pre_approved"

        return reverse(
            url_string,
            args=[
                self.stepper.proposal.pk,
            ],
        )

    def make_stepper_item(
        self,
    ):
        self.recursion_marker = False

        def submittable():
            """
            Return a single error if the proposal is not submittable,
            avoiding recursion in error fetching.
            """
            if self.recursion_marker:
                # This function will only return errors once
                return []
            self.recursion_marker = True
            all_errors = self.stepper.get_form_errors()
            if all_errors:
                return [_("Aanvraag bevat nog foutmeldingen")]
            return []

        item = super().make_stepper_item()
        item.get_checker_errors = submittable
        return item

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["proposal"] = self.proposal
        kwargs["request"] = self.stepper.request
        return kwargs
