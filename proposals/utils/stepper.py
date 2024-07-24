from copy import copy

from django.urls import reverse
from django.template import loader, Template
from django.core.exceptions import ImproperlyConfigured

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


class StepperItem:
    """
    Represents an item in the stepper
    """

    stepper_title = "Stepper item"
    stepper_children = []
    available = True

    @property
    def stepper_url(self):
        return "#"

    def is_current(self, request):
        """
        Returns True if this item represents the page the user
        is currently on.
        """
        return False

class FormPage(StepperItem):

    def instantiate(self):
        pass

class ViewPage(StepperItem):

    view_class = None

    def is_current(self, request):
        breakpoint()
        return True

    def css_classes(self):
        classes = set()
        if self.is_current():
            classess.add("current")


class FirstPage(ViewPage):

    view_class = ProposalUpdate


class Page(StepperItem):
    """Represents both a visitable page in the proposal form,
    and an entry in the stepper."""

    def __init__(self, proposal, current=None):
        """Initialize the page with the proposal object"""
        self.proposal = proposal

    def collect_errors(self):
        return []

    def is_complete(self):
        return self.collect_errors == []

    def get_url(self):
        return reverse(
            "proposals:update",
            kwargs={
                "pk": self.proposal.pk,
            },
        )

