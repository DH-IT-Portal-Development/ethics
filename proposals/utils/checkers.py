from braces.forms import UserKwargModelFormMixin

from django.utils.translation import gettext as _
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from proposals import forms

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
        process. It finall returns a list of checkers with which to continue
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
    form_class = forms.ProposalForm

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
    form_class = forms.ResearcherForm

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
    form_class = forms.OtherResearchersForm

    def check(self):
        self.stepper.items.append(self.make_stepper_item())
        return []

    def get_url(self):
        return reverse(
            "proposals:other_researchers",
            args=(self.proposal.pk,),
        )
