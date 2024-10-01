from django.core.exceptions import ImproperlyConfigured
from braces.forms import UserKwargModelFormMixin

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

    def __init__(self, stepper, parent=None, title=None, location=None):
        self.stepper = stepper
        self.proposal = stepper.proposal
        self.children = []
        self.parent = parent
        self.is_expanded = False
        self.css_classes = set()
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
        return ""

    def get_errors(self, include_children=False):
        return []

    def get_ancestors(self):
        """
        Returns a list of all ancestors, including itself, from young to old.
        """
        ancestors = []
        ancestors.append(self)
        if not self.parent:
            return ancestors
        else:
            parent = self.parent
            ancestors.append(parent)
            while parent.parent:
                parent = parent.parent
                ancestors.append(parent)
        return ancestors

    def is_current(self, request):
        """
        Returns True if this item represents the page the user
        is currently on and adds the active class to the item's
        self.css_classes set. This gets called when building the stepper,
        until is_current returns True.
        """
        if request.path == self.get_url():
            return True
        return False

    def is_disabled(self):
        if not self.get_url():
            return True
        return False

    def build_css_classes(self):
        """
        A method to be overwritten by child classes to append to an item's
        self.css_classes attribute. It returns nothing but appends to the set
        self.css_classes. It gets called in self.get_css_classes.
        """
        pass

    def get_css_classes(self):
        """
        A methods that calls self.build_css_classes, to complete the list
        self.css_classes and formats this list as a space-seperated string,
        to be used for rendering.
        """
        self.build_css_classes()
        return " ".join(self.css_classes)


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

    def get_errors(self, include_children=True):
        """
        ContainerItems will only check its children for errors.
        """
        errors = []
        if include_children:
            for child in self.children:
                errors += child.get_errors(include_children=True)
        return errors

    def build_css_classes(self):
        if self.get_errors(include_children=True):
            self.css_classes.add("incomplete")
        else:
            self.css_classes.add("complete")


class ModelFormChecker(
    Checker,
):
    """
    A checker base that makes it as easy as possible to go from checking
    a ModelForm to making a stepper item.
    """

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
            form_kwargs=self.get_form_kwargs(),
            url_func=self.get_url,
            location=self.location,
        )
        return stepper_item

    def get_form_object(
        self,
    ):
        # Overwrite method for other objects
        return self.proposal

    def get_form_kwargs(self):
        # Overwrite for specific form_kwargs

        return {}


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
        self.form_kwargs = kwargs.pop(
            "form_kwargs",
        )
        get_url = kwargs.pop(
            "url_func",
            None,
        )
        get_checker_errors = kwargs.pop(
            "error_func",
            None,
        )
        if get_url:
            self.get_url = get_url
        if get_checker_errors:
            self.get_checker_errors = get_checker_errors
        return super().__init__(*args, **kwargs)

    @property
    def model_form(self):
        """
        This property is used to access the bound ModelForm and its errors.
        self.instantiated_form can be set by hand (e.g. by a checker) to bypass
        default form instantiation.
        """
        if not hasattr(self, "instantiated_form"):
            self.instantiated_form = self.instantiate_form()
        return self.instantiated_form

    def get_form_object(self):
        """
        Override this for modelforms that don't relate to a
        Proposal model.
        """
        return self.proposal

    def get_form_kwargs(self):
        """
        This method can be overidden to provide extra kwargs to the form. But
        kwargs that pop up often can also be added to this base class.
        """
        kwargs = self.form_kwargs
        if issubclass(self.form_class, UserKwargModelFormMixin):
            kwargs["user"] = self.stepper.request.user
        return kwargs

    def instantiate_form(self):
        if not self.form_class:
            raise ImproperlyConfigured("form_class must be defined")
        kwargs = self.get_form_kwargs()
        model_form = self.form_class(
            instance=self.form_object,
            **kwargs,
        )
        return model_form

    def get_errors(self, include_children=False):
        """
        By default, this returns the errors of the instantiated form and,
        optionally, its children. This then gets evaluated as a boolean.
        By passing a custom get_checker_errors function
        from the checker, custom errors also be added.
        """
        errors = []
        errors += self.model_form.errors

        if hasattr(self, "get_checker_errors"):
            errors += self.get_checker_errors()
        if include_children and self.children:
            for child in self.children:
                errors += child.get_errors(include_children=True)
        return errors

    def build_css_classes(self):
        """
        If an item is collapsed, its completeness also depends on
        its children, otherwise, it only depends on the form the
        the item represents.
        """
        if not self.is_expanded and self.children:
            if self.get_errors(include_children=True):
                self.css_classes.add("incomplete")
            else:
                self.css_classes.add("complete")
        elif self.get_errors():
            self.css_classes.add("incomplete")
        else:
            self.css_classes.add("complete")


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
