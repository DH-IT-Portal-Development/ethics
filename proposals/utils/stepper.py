from proposals.models import Proposal
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


class Stepper(renderable):

    template_name = "base/stepper.html"
    starting_checkers = []

    def __init__(self, proposal, current=None):

        self.proposal = proposal
        self.current = current
        self.check_all(self.starting_checkers)

    def get_context_data(self):
        return {"stepper": self}

    def get_resume_url(self):
        """
        Returns the url of the first page that requires attention,
        that being either a page with an error or an incomplete page.
        """
        pages = self.collect_pages()

        for page in flatten(pages):
            if not page.is_complete:
                return page.get_url()

    def collect_items(self):
        some_pages = []
        for i in range(5):
            some_pages.append(
                Page(self.proposal)
            )
        first_page = FirstPage()
        some_pages.append(first_page)
        return some_pages

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

