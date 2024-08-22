from braces.forms import UserKwargModelFormMixin

from django.utils.translation import gettext as _
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from proposals import forms as proposal_forms
from studies import forms as study_forms

from .stepper_helpers import RegularProposalLayout, PlaceholderItem, StepperItem

class BaseStepperComponent:

    def __init__(self, stepper, parent=None):
        self.stepper = stepper
        self.proposal = stepper.proposal
        self.parent = parent

class Checker(
        BaseStepperComponent,
):

    def __call__(self, *args, **kwargs):
        """
        This class may be called to initialize it when it is
        already initialized. For now, we don't do anything with this
        and pretend we just got initialized.
        """
        return self

    def check(self):
        """
        This method gets called to process an item in the proposal creation
        process. It finally returns a list of checkers with which to continue
        the checking process. This list can be empty.
        """
        return []

class ModelFormChecker(
        Checker,
):

    form_class = None
    title = None

    def __init__(self, *args, **kwargs):
        if not self.form_class:
            raise ImproperlyConfigured(
                "form_class must be defined"
            )
        return super().__init__(*args, **kwargs)

    def make_stepper_item(self):
        if not self.title:
            raise ImproperlyConfigured(
                "title must be defined"
            )
        stepper_item = ModelFormItem(
            self.stepper,
            title=self.title,
            parent=self.parent,
            form_object=self.get_form_object(),
            form_class=self.form_class,
            url_func=self.get_url,
        )
        return stepper_item

    def get_form_object(self,):
        # Overwrite method for other objects
        return self.proposal


class ProposalTypeChecker(
        Checker,
        BaseStepperComponent,
):

    def check(self):
        # TODO: check stepper.proposal_type_hint
        # and proposal.is_pre_approved etc. for non-standard layouts
        return self.regular_proposal()

    def regular_proposal(self):
        self.stepper.base_layout = RegularProposalLayout
        return [ProposalCreateChecker]


class ModelFormItem(
        StepperItem,
):

    def __init__(self, *args, **kwargs):
        self.form_class = kwargs.pop(
            "form_class",
        )
        self.form_object = kwargs.pop(
            "form_object",
        )
        get_url = kwargs.pop(
            "url_func",
            None,
        )
        if get_url:
            self.get_url = get_url
        return super().__init__(*args, **kwargs)

    @property
    def model_form(self):
        if not self.form_class:
            raise ImproperlyConfigured(
                "form_class must be defined"
            )
        if not hasattr(self, instantiated_form):
            self.instantiated_form = self.instantiate_form()
        return self.instantiated_form

    def get_form_object(self):
        return self.proposal

    def get_form_kwargs(self):
        kwargs = {}
        if issubclass(self.form_class, UserKwargModelFormMixin):
            kwargs["user"] = self.stepper.request.user
        return kwargs

    def instantiate_form(self):
        kwargs = self.get_form_kwargs()
        model_form = self.form_class(
            instance=self.get_form_object(),
            **kwargs,
        )
        self.form_errors = model_form.errors
        return model_form

    def get_errors(self):
        return self.form_errors

class ContainerItem(
    StepperItem,
):
    """
    A basic stepper item that is nothing more than a parent for its
    children. Its url will try to redirect to its first child.
    """

    def get_url(self):
        try:
            url = self.children[0].get_url()
            return url
        except:
            return ""

    def is_current(self, request):
        """
        Because container items by default refer to their first child,
        we say they are never current. The child is.
        """
        return False

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
        if self.proposal.pk:
            return reverse(
                "proposals:update",
                args=[self.proposal.pk],
            )
        return reverse(
            "proposals:create",
        )

    def check(self):
        self.parent = BasicDetailsItem(self.stepper)
        self.stepper.items.append(self.parent)
        if self.proposal.pk:
            return self.proposal_exists()
        return self.new_proposal()

    def new_proposal(self):
        self.stepper.items.append(
            self.make_stepper_item()
        )
        placeholders = [
            PlaceholderItem(
                self.stepper,
                title=_("Onderzoeker"),
                parent=self.parent,
            ),
            PlaceholderItem(
                self.stepper,
                title=_("Andere onderzoekers"),
                parent=self.parent,
            ),
        ]
        self.stepper.items += placeholders
        return []

    def proposal_exists(self):
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
        return [
            OtherResearchersChecker(
                self.stepper,
                parent=self.parent
            )
        ]

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

    def get_wmo(self,):
        if hasattr(
            self.proposal,
            "wmo",
        ):
            return self.proposal.wmo
        return None

    def get_url(self,):
        if self.wmo:
            return reverse(
                "proposals:wmo_update",
                args=[self.wmo.pk],
            )
        else:
            return reverse(
                "proposals:wmo_create",
                args=[self.proposal.pk],
            )

    def wmo_exists(self,):
        return hasattr(
            self.proposal,
            "wmo",
        )


class WMOChecker(
        Checker,
):

    def check(self,):
        self.item = WMOItem(self.stepper)
        self.stepper.items.append(self.item)
        if self.item.wmo:
            return self.check_wmo()
        else:
            return []

    def check_wmo(self,):
        """
        This method should check the correctness of the
        WMO object.
        """
        # Just assume any WMO is correct as long as it exists
        if self.item.wmo:
            return [TrajectoriesChecker]
        return [] # TODO next item


class TrajectoriesItem(
        StepperItem,
):
    title = _("Trajecten")
    location = "studies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_url(self,):
        return reverse(
            "proposals:study_start",
            args=[self.proposal.pk],
        )

class TrajectoriesChecker(
        Checker,
):

    def check(self,):
        self.item = TrajectoriesItem(self.stepper)
        self.stepper.items.append(self.item)
        sub_items = [
            self.make_study_checker(s) for s in self.get_studies()
        ]
        return sub_items + self.remaining_checkers()

    def make_study_checker(self, study):
        return StudyChecker(
            self.stepper,
            parent=self.item,
            study=study,
        )

    def remaining_checkers(self,):
        return []

    def get_studies(self,):
        proposal = self.stepper.proposal
        return list(
            proposal.study_set.all(),
        )

class StudyChecker(
    Checker,
):
    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(self,):
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
        return checkers + self.determine_study_checkers(self.study)

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

    def __init__(self, *args, **kwargs,):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(self,):
        self.stepper.items.append(
            self.make_stepper_item()
        )
        return []

    def get_url(self,):
        return reverse(
            "studies:update",
            args=[self.study.pk,],
        )

class DesignChecker(
        ModelFormChecker,
):
    title = _("Ontwerp")
    form_class = study_forms.StudyDesignForm

    def __init__(self, *args, **kwargs,):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(self,):
        self.stepper.items.append(
            self.make_stepper_item()
        )
        return []

    def get_url(self,):
        return reverse(
            "studies:design",
            args=[self.study.pk,],
        )

class UpdateOrCreateChecker(
        ModelFormChecker,
):
    """
    A variation on the ModelFormChecker designed for
    forms like the InterventionForm, which link either
    to a create or update view depending on if they exist
    already.

    If the object in question exists, this class acts like
    a normal ModelFormChecker. Otherwise it provides a factory
    for a PlaceholderItem that links to the CreateView.
    """

    def make_stepper_item(self,):
        if self.object_exists():
            return super().make_stepper_item()
        return self.make_placeholder_item()

    def make_placeholder_item(self,):
        item = PlaceholderItem(
            self.stepper,
            title=self.title,
            parent=self.parent,
        )
        item.get_url = self.get_create_url()

    def object_exists(self,):
        # By default, assume the object exists
        return True

    def get_create_url(self,):
        return ""

    def get_update_url(self,):
        return ""


class InterventionChecker(
        Checker,
):
    def __init__(self, *args, **kwargs,):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(self,):
        return []


class ObservationChecker(
        Checker,
):
    def __init__(self, *args, **kwargs,):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(self,):
        return []


class SessionsChecker(
        Checker,
):
    def __init__(self, *args, **kwargs,):
        self.study = kwargs.pop("study")
        return super().__init__(*args, **kwargs)

    def check(self,):
        return []
