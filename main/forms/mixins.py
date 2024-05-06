from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.forms.fields import Field, FileField
from django.forms.models import InlineForeignKeyField, construct_instance
from django.forms.utils import ErrorDict
from django.utils.translation import gettext as _


class SoftValidationMixin:
    """
    This mixin will allow a form to submit even if specified fields have
    validator errors.
    """

    # Disable the default TemplatedForm behavior of showing valid fields, it will be even more confusing
    show_valid_fields = False

    _soft_validation_fields = []

    def __init__(self, *args, **kwargs):
        super(SoftValidationMixin, self).__init__(*args, **kwargs)

        # If we have an existing instance and we're not POSTing,
        # run a initial clean
        if self.instance.pk and "data" not in kwargs:
            self.initial_clean()

    def initial_clean(self):
        """
        Cleans all of self.initial and populates self._errors
        """
        self._errors = ErrorDict()

        reset_cleaned = False
        if not hasattr(self, "cleaned_data"):
            reset_cleaned = True
            self.cleaned_data = {}

        self._initial_clean_fields()
        self._initial_clean_form()
        self._initial_post_clean()

        if reset_cleaned:
            del self.cleaned_data

    def _initial_clean_fields(self):
        for field_name, value in self.initial.items():
            if field_name in self.fields:
                field = self.fields[field_name]
            else:
                continue

            try:
                if isinstance(field, FileField):
                    val = field.clean(value, value)
                else:
                    val = field.clean(value)
                if hasattr(self, "clean_%s" % field):
                    val = getattr(self, "clean_%s" % field)()

                self.cleaned_data[field_name] = val
            except ValidationError as e:
                self.add_error(field_name, e)

    def _initial_clean_form(self):
        try:
            self.clean()
        except ValidationError as e:
            self.add_error(None, e)

    def mark_soft_required(self, data, *fields):
        """
        This can be used to validate a field as required, without actually
        making it required in the corresponding model.


        """
        for field in fields:
            if field not in self.fields:
                raise ImproperlyConfigured(
                    "{} is not a field of {}!".format(field, self.__class__.__name__)
                )

            if field not in data or not data[field]:
                self.add_error(field, _("Dit veld is verplicht."))

    def _initial_post_clean(self):
        opts = self._meta

        exclude = self._get_validation_exclusions()

        # Foreign Keys being used to represent inline relationships
        # are excluded from basic field value validation. This is for two
        # reasons: firstly, the value may not be supplied (#12507; the
        # case of providing new values to the admin); secondly the
        # object being referred to may not yet fully exist (#12749).
        # However, these fields *must* be included in uniqueness checks,
        # so this can't be part of _get_validation_exclusions().
        for name, field in self.fields.items():
            if isinstance(field, InlineForeignKeyField):
                exclude.append(name)

        try:
            self.instance = construct_instance(
                self, self.instance, opts.fields, opts.exclude
            )
        except ValidationError as e:
            self._update_errors(e)

        try:
            self.instance.full_clean(exclude=exclude, validate_unique=False)
        except ValidationError as e:
            self._update_errors(e)

        # Validate uniqueness if needed.
        self.validate_unique()

    @property
    def _hard_errors(self):
        return [
            x
            for x in self.errors.items()
            if x[0] not in self.get_soft_validation_fields()
        ]

    def get_soft_validation_fields(self):
        return self._soft_validation_fields

    def save(self, commit=True):
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.

        This method is modified to only fail on hard errors
        """
        if self._hard_errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance

    def is_valid(self):
        """This method is modified to only return False on hard errors"""
        return self.is_bound and not self._hard_errors
