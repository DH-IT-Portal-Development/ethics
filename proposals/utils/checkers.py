from braces.forms import UserKwargModelFormMixin

from django.utils.translation import gettext as _
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from proposals import forms

from .stepper_helpers import RegularProposalLayout, PlaceholderItem, StepperItem

class BaseChecker:

    def __init__(self, stepper, parent=None):
        self.stepper = stepper
        self.proposal = stepper.proposal
        self.parent = parent

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


class ProposalTypeChecker(
        BaseChecker,
):

    def check(self):
        # TODO: check stepper.proposal_type_hint
        # and proposal.is_pre_approved etc. for non-standard layouts
        return self.regular_proposal()

    def regular_proposal(self):
        self.stepper.base_layout = RegularProposalLayout
        return [ProposalCreateChecker]


class ModelFormChecker(
        BaseChecker,
):
    form_class = None

    def __init__(self, stepper, parent=None):
        super().__init__(stepper, parent=parent)
        if not self.form_class:
            raise ImproperlyConfigured(
                "form_class must be defined"
            )
        self.model_form = self.instantiate_form()

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
        StepperItem,
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
            self,
        )
        return []

    def proposal_exists(self):
        self.stepper.items.append(
            self,
        )
        return [
            ResearcherChecker(
                self.stepper,
                parent=self.parent,
            )
        ]

class ModelFormItem(
        StepperItem,
):
    def __init__(self, model_form):
        self.model_form = model_form

class ResearcherChecker(
        ModelFormChecker,
        StepperItem,
):
    title = _("Onderzoeker")
    form_class = forms.ResearcherForm

    def check(self):
        self.stepper.items.append(self)
        return []

    def get_url(self):
        return reverse(
            "proposals:researcher",
            args=(self.proposal.pk,),
        )
