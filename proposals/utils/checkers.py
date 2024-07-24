from django.utils.translation import gettext as _
from django.core.exceptions import ImproperlyConfigured

from proposals.forms import ProposalForm

from .stepper_helpers import RegularProposalLayout, PlaceholderItem, StepperItem

class BaseChecker:

    def __init__(self, stepper):
        self.stepper = stepper
        self.proposal = stepper.proposal

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

    def __init__(self, stepper):
        super().__init__(stepper)
        if not self.form_class:
            raise ImproperlyConfigured(
                "form_class must be defined"
            )
        self.model_form = self.instantiate_form()

    def get_form_object(self):
        return self.proposal

    def instantiate_form(self):
        model_form = self.form_class(
            instance=self.get_form_object(),
        )
        self.form_errors = model_form.errors
        return model_form

class BasicDetailsItem(
    StepperItem,
):
    title = "Basic details inserted"
    location = "create"

    def get_url(self):
        try:
            url = self.children[0].get_url()
            return url
        except:
            return "#"

class ProposalCreateChecker(
        ModelFormChecker,
):
    form_class = ProposalForm

    def check(self):
        self.parent_item = BasicDetailsItem()
        self.stepper.items.append(self.parent_item)
        if self.proposal.pk:
            return self.proposal_exists()
        return self.new_proposal()

    def new_proposal(self):
        self.stepper.items.append(
            PlaceholderItem(
                name="Create_proposal",
                parent=self.parent_item,
            )
        )
        return []

    def proposal_exists(self):
        self.stepper.items.append(
            PlaceholderItem(
                name="Update_proposal",
                parent=self.parent_item,
            )
        )
        return []
