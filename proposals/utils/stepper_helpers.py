from copy import copy

from django.utils.translation import gettext as _
from django.urls import reverse

from main.utils import renderable

class StepperItem(
        renderable,
):
    """
    Represents an item in the stepper
    """

    template_name = "base/stepper_item.html"
    title = "Stepper item"
    location = None

    def __init__(self, stepper, parent=None, disabled=False, title=None, location=None):
        self.stepper = stepper
        self.proposal = stepper.proposal
        self.children = []
        self.parent = parent
        self.available = False
        self.disabled = disabled
        # Don't override default location if not provided explicitly
        if location:
            self.location = location
        if title:
            self.title = title

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {
                "item": self,
            }
        )
        return context

    def get_url(self):
        return "#"

    def get_errors(self):
        return []

    def css_classes(
        self,
    ):
        classes = []
        if self.is_current(self.stepper.request):
            classes.append(
                "active",
            )
        if self.disabled:
            classes.append(
                "disabled",
            )
        return " ".join(classes)

    def is_current(self, request):
        """
        Returns True if this item represents the page the user
        is currently on.
        """
        if request.path == self.get_url():
            return True
        return False


class PlaceholderItem(StepperItem):

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def get_url(
        self,
    ):
        return ""


def flatten(lst):
    if lst == []:
        return lst
    first_item = lst[0]
    rest = lst[1:]
    if type(first_item) is list:
        return flatten(first_item) + flatten(rest)
    return [first_item] + flatten(rest)


class Layout:

    def __init__(self, stepper, base_layout):
        self.stepper = stepper
        self.layout = copy(base_layout)

    def insert_item(self, new_item):
        if new_item.parent:
            return self.insert_child(new_item)
        location = new_item.location
        for index, item in enumerate(copy(self.layout)):
            if type(item) is not tuple:
                continue
            if location == item[0]:
                self.layout.insert(index, new_item)
                self.layout.remove(item)
                return
        self.layout.append(new_item)

    def insert_placeholders(self):
        for index, item in enumerate(copy(self.layout)):
            if isinstance(item, StepperItem):
                continue
            placeholder = PlaceholderItem(
                self.stepper,
                title=item[1],
            )
            self.layout.insert(index, placeholder)
            self.layout.remove(item)

    def insert_child(self, item):
        item.parent.children.append(item)

    def make_stepper(self):
        self.insert_placeholders()
        return self.layout


RegularProposalLayout = [
    ("create", _("Basisgegevens")),
    ("wmo", _("WMO")),
    ("studies", _("Trajecten")),
    ("attachments", _("Documenten")),
    ("data_management", _("Datamanagement")),
    ("submit", _("Indienen")),
]
