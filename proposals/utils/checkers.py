from django.utils.translation import gettext as _
from django.urls import reverse

from proposals import forms as proposal_forms
from studies import forms as study_forms
from interventions import forms as intervention_forms
from observations import forms as observation_forms
from tasks import forms as tasks_forms

from tasks.views import task_views, session_views
from tasks.models import Task, Session

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
        from .stepper import RegularProposalLayout, PreApprProposalLayout, PreAssProposalLayout

        if self.proposal.is_pre_approved:
            self.stepper.layout = PreApprProposalLayout
            return [PreApprProposalCreateChecker]
        elif self.proposal.is_pre_assessment:
            self.stepper.layout = PreAssProposalLayout
            return [PreAssProposalCreateChecker]
        else:
            self.stepper.layout = RegularProposalLayout
            return [ProposalCreateChecker]


class BasicDetailsItem(
    ContainerItem,
):
    title = _("Basisgegevens")
    location = "create"


class ProposalCreateChecker(
    ModelFormChecker,
):
    title = _("Start")
    form_class = proposal_forms.ProposalForm

    def get_url(self):
        return reverse(
            "proposals:update",
            args=[self.proposal.pk],
        )

    def check(self):
        self.parent = BasicDetailsItem(self.stepper)
        self.stepper.items.append(self.parent)
        stepper_item = ModelFormItem(
            self.stepper,
            title=self.title,
            parent=self.parent,
            form_object=self.proposal,
            form_class=self.form_class,
            url_func=self.get_url,
        )
        self.stepper.items.append(
            stepper_item,
        )
        return [
            ResearcherChecker(
                self.stepper,
                parent=self.parent,
            )
        ]


class ResearcherChecker(
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
        if self.proposal.is_pre_assessment:
            return [
                GoalChecker(
                    self.stepper,
                    parent=self.parent,
                )
            ]
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
        return [WMOChecker]

    def get_url(self):
        return reverse(
            "proposals:research_goal",
            args=(self.proposal.pk,),
        )


class WMOItem(
    StepperItem,
):
    location = "wmo"
    title = _("WMO")

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.proposal = self.stepper.proposal
        self.wmo = self.get_wmo()

    def get_wmo(
        self,
    ):
        if hasattr(
            self.proposal,
            "wmo",
        ):
            return self.proposal.wmo
        return None

    def get_url(
        self,
    ):
        if self.proposal.is_pre_assessment:
            pre_suffix = "_pre"
        else:
            pre_suffix = ""
        if self.wmo:
            return reverse(
                f"proposals:wmo_update{pre_suffix}",
                args=[self.wmo.pk],
            )
        else:
            return reverse(
                f"proposals:wmo_create{pre_suffix}",
                args=[self.proposal.pk],
            )


class WMOChecker(
    Checker,
):

    def check(
        self,
    ):
        self.item = WMOItem(self.stepper)
        self.stepper.items.append(self.item)
        if self.item.wmo:
            return self.check_wmo()
        else:
            return []

    def check_wmo(
        self,
    ):
        """
        This method should check the correctness of the
        WMO object.
        """
        #TODO: implement WmoApplicationChecker
        # Just assume any WMO is correct as long as it exists
        if self.proposal.is_pre_assessment:
            return [SubmitChecker]
        return [TrajectoriesChecker]


class TrajectoriesChecker(
    ModelFormChecker,
):
    form_class = proposal_forms.StudyStartForm
    title = _("Trajecten")
    location = "studies"

    def check(
        self,
    ):
        self.item = self.make_stepper_item()
        self.stepper.items.append(self.item)
        sub_items = [self.make_study_checker(s) for s in self.get_studies()]
        return sub_items + self.remaining_checkers()

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
            DocumentsChecker,
            DataManagementChecker,
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
            DesignChecker(
                self.stepper,
                study=self.study,
                parent=self.current_parent,
            ),
        ]
        end_checker = StudyEndChecker(
            self.stepper,
            study=self.study,
            parent=self.current_parent,
        )
        return checkers + self.determine_study_checkers(self.study) + [end_checker]

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


class ParticipantsChecker(
    ModelFormChecker,
):
    title = _("Deelnemers")
    form_class = study_forms.StudyForm

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

    def get_url(
        self,
    ):
        return reverse(
            "studies:update",
            args=[
                self.study.pk,
            ],
        )


class DesignChecker(
    ModelFormChecker,
):
    title = _("Ontwerp")
    form_class = study_forms.StudyDesignForm

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
    ModelFormChecker,
):
    title = _("Afronding")
    form_class = study_forms.StudyEndForm

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
        item = super().make_stepper_item()

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


class DocumentsChecker(
    Checker,
):
    def make_stepper_item(
        self,
    ):
        return ContainerItem(
            self.stepper,
            title=_("Documenten"),
            location="attachments",
        )

    def check(
        self,
    ):
        item = self.make_stepper_item()
        self.stepper.items.append(item)
        return [
            TranslationChecker(
                self.stepper,
                parent=item,
            ),
            AttachmentsChecker(
                self.stepper,
                parent=item,
            ),
        ]


class TranslationChecker(
    ModelFormChecker,
):
    form_class = proposal_forms.TranslatedConsentForms
    title = _("Vertalingen")
    location = "data_management"

    def check(
        self,
    ):
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


class AttachmentsChecker(
    Checker,
):

    def check(
        self,
    ):
        self.stepper.items.append(self.make_stepper_item())
        return []

    def make_stepper_item(self):
        url = reverse(
            "proposals:consent",
            args=[self.stepper.proposal.pk],
        )
        item = PlaceholderItem(
            self.stepper,
            title=_("Documenten beheren"),
            parent=self.parent,
        )
        item.get_url = lambda: url
        return item


class DataManagementChecker(
    ModelFormChecker,
):
    title = _("Data management")
    form_class = proposal_forms.ProposalDataManagementForm
    location = "data_management"

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
        return reverse(
            "proposals:data_management",
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
        return reverse(
            "proposals:submit",
            args=[
                self.stepper.proposal.pk,
            ],
        )
