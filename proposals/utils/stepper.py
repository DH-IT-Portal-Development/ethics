from proposals.models import Proposal
from django.urls import reverse
from django.template import loader, Template
from django.core.exceptions import ImproperlyConfigured

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

    def __init__(self, proposal, current=None):

        self.proposal = proposal
        self.current = current

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
        return some_pages


class StepperContextMixin:
    """
    Includes a stepper object in the view's context
    """

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Try to determine proposal
        if hasattr(self, "proposal"):
            proposal = self.proposal
        else:
            proposal = Proposal.objects.get(pk=self.kwargs.get("pk"))
        # Initialize and insert stepper object
        context["stepper"] = Stepper(proposal)
        return context


class Page:
    """Represents both a visitable page in the proposal form,
    and an entry in the stepper."""

    stepper_title = "Stepper item"

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

