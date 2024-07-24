from copy import copy

from django.urls import reverse
from django.template import loader, Template
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _

from proposals.models import Proposal
from proposals.forms import ProposalForm

from proposals.views.proposal_views import ProposalUpdate

def flatten(lst):
    if lst == []:
        return lst
    first_item = lst[0]
    rest = lst[1:]
    if type(first_item) is list:
        return flatten(first_item) + flatten(rest)
    return [first_item] + flatten(rest)


class renderable:

    def get_context_data(self):
        return {}

    def render(self, context={}):
        template = loader.get_template(self.template_name)
        context.update(self.get_context_data())
        return template.render(context.flatten())

class Layout:

    def __init__(self, layout):
        self.layout = layout

    def insert_item(self, new_item):
        if new_item.parent:
            self.insert_child(new_item)
        location = new_item.location
        for index, item in enumerate(copy(self.layout)):
            if location == item[0]:
                self.layout.insert(new_item, index)
                self.layout.remove(item)
                return
        self.layout.append(new_item)

    def insert_placeholders(self):
        for index, item in enumerate(copy(self.layout)):
            if isinstance(item, StepperItem):
                continue
            placeholder = PlaceholderItem(
                item[1],
            )
            self.layout.insert(index, placeholder)
            self.layout.remove(item)

    def make_stepper(self):
        self.insert_placeholders()
        return self.layout


RegularProposalLayout = Layout([
    ("create", _("Basisgegevens")),
    ("wmo", _("WMO")),
    ("studies", _("Trajecten")),
    ("attachments", _("Documenten")),
    ("data_management", _("Datamanagement")),
    ("submit", _("Indienen")),
])

class Stepper(renderable):

    template_name = "base/stepper.html"

    def __init__(self, proposal, current=None):

        self.proposal = proposal
        self.current = current
        self.starting_checkers = [
            ProposalTypeChecker,
        ]
        self.items = []
        self.check_all(self.starting_checkers)

    def get_context_data(self):
        return {"stepper": self}

    def get_resume_url(self):
        """
        Returns the url of the first page that requires attention,
        that being either a page with an error or an incomplete page.
        """
        for item in flatten(self.items):
            if not item.is_complete:
                return item.get_url()

    def collect_items(self):
        if not hasattr(self, "layout"):
            raise RuntimeError(
                "Layout was never defined for this stepper",
            )
        for item in self.items:
            self.layout.insert(item)
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
        self.stepper.layout = RegularProposalLayout
        return []

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

class ProposalCreateChecker(
        ModelFormChecker,
):
    form_class = ProposalForm

    def check(self):
        return []

class StepperItem:
    """
    Represents an item in the stepper
    """

    title = "Stepper item"
    children = []
    available = True

    @property
    def get_url(self):
        return "#"

    def is_current(self, request):
        """
        Returns True if this item represents the page the user
        is currently on.
        """
        return False

class PlaceholderItem(StepperItem):

    def __init__(self, name):
        self.title = name

