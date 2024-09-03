from copy import copy

from django.utils.translation import gettext as _
from django.urls import reverse

from main.utils import renderable


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
        process. It finally returns a list of checkers with which to continue
        the checking process. This list can be empty.
        """
        return []


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


class ModelFormChecker(
    Checker,
):

    form_class = None
    title = None
    location = None

    def __init__(self, *args, **kwargs):
        if not self.form_class:
            raise ImproperlyConfigured("form_class must be defined")
        return super().__init__(*args, **kwargs)

    def make_stepper_item(self):
        if not self.title:
            raise ImproperlyConfigured("title must be defined")
        stepper_item = ModelFormItem(
            self.stepper,
            title=self.title,
            parent=self.parent,
            form_object=self.get_form_object(),
            form_class=self.form_class,
            url_func=self.get_url,
            location=self.location,
        )
        return stepper_item

    def get_form_object(
        self,
    ):
        # Overwrite method for other objects
        return self.proposal


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
            raise ImproperlyConfigured("form_class must be defined")
        if not hasattr(self, "instantiated_form"):
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


class UpdateOrCreateChecker(
    ModelFormChecker,
):
    """
    A variation on the ModelFormChecker designed for
    forms like the InterventionForm, which link either
    to a create or update view depending on if they exist
    already.

    If the object in question exists, this class acts like
    a normal ModelFormChecker. Otherwise it provides a factory
    for a PlaceholderItem that links to the CreateView.
    """

    def make_stepper_item(
        self,
    ):
        if self.object_exists():
            return super().make_stepper_item()
        return self.make_placeholder_item()

    def make_placeholder_item(
        self,
    ):
        item = PlaceholderItem(
            self.stepper,
            title=self.title,
            parent=self.parent,
        )
        item.get_url = self.get_create_url
        return item

    def object_exists(
        self,
    ):
        # By default, assume the object exists
        return True

    def get_url(self):
        return self.get_update_url()

    def get_create_url(
        self,
    ):
        return ""

    def get_update_url(
        self,
    ):
        return ""

