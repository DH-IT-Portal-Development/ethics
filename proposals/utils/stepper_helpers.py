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

