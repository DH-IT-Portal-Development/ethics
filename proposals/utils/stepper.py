from copy import copy

from django.urls import reverse
from django.template import loader, Template
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _

from proposals.models import Proposal
from proposals.forms import ProposalForm
from proposals.views.proposal_views import ProposalUpdate

from .stepper_helpers import (
    PlaceholderItem,
    StepperItem,
    flatten,
    renderable,
    Layout,
)

from .checkers import ProposalTypeChecker


class Stepper(renderable):

    template_name = "base/stepper.html"

    def __init__(
        self,
        proposal,
        current=None,
        proposal_type_hint=None,
        request=None,
    ):
        self.proposal = proposal
        self.current = current
        self.starting_checkers = [
            ProposalTypeChecker,
        ]
        self.request = request
        self.proposal_type_hint = proposal_type_hint
        self.items = []
        self.check_all(self.starting_checkers)

    def get_context_data(self):
        context = super().get_context_data()
        bubble_list = [
            "stepper-bubble-largest",
            "stepper-bubble-large",
            "stepper-bubble-medium",
            "stepper-bubble-small",
            "stepper-bubble-smallest",
        ]
        context.update(
            {
                "stepper": self,
                "bubble_size": bubble_list,
            }
        )
        return context

    def get_resume_url(self):
        """
        Returns the url of the first page that requires attention,
        that being either a page with an error or an incomplete page.
        """
        for item in flatten(self.items):
            if not item.is_complete:
                return item.get_url()

    def collect_items(self):
        if not hasattr(self, "base_layout"):
            raise RuntimeError(
                "Base layout was never defined for this stepper",
            )
        self.layout = Layout(self, self.base_layout)
        for item in self.items:
            self.layout.insert_item(item)
        return self.layout.make_stepper()

    def check_all(self, next_checkers):
        # No more checkers means we are done
        if next_checkers == []:
            return True
        # Instantiate next checker
        # and give it access to the stepper
        current = next_checkers.pop(0)(self)
        # Run the check method
        # and gather new checkers from its output
        new_checkers = current.check()
        # Combine the lists, new checkers come first
        next_checkers = new_checkers + next_checkers
        # Recurse until next_checkers is empty
        return self.check_all(next_checkers)

    def has_multiple_studies(
        self,
    ):
        """
        Returns True if the proposal has more than one trajectory (study).
        """
        num_studies = self.proposal.study_set.count()
        return num_studies > 1
