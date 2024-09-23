from django.views import generic
from django.forms import forms, ModelForm
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from .models import Attachment

# Create your views here.

class AttachmentForm(ModelForm):

    class Meta:
        model = Attachment
        fields = [
            "kind",
            "upload",
            "name",
            "comments",
        ]

    def __init__(self, kind=None, *args, **kwargs):
        self.kind = kind
        return super().__init__(*args, **kwargs)

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if self.kind:
            initial["kind"] = self.kind
        return initial

class AttachmentCreateView(generic.CreateView):
    """Generic create view to create a new attachment. Both other_model and
    template_name should be provided externally, either through the URL
    definition or through subclassing."""

    model = None
    form_class = None
    template_name = None

    other_model = None
    other_field_name = "attachments"
    other_pk_kwarg = "other_pk"

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def save(self, form):
        result = super().save(form)
        self.attach(form.instance)
        return result

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "kind" in self.kwargs.keys():
            kwargs["kind"] = self.kwargs.get("kind")
        return kwargs

    def attach(self, attachment):
        if self.other_model is None:
            raise ImproperlyConfigured(
                "Please provide an other_model as a target for "
                "this attachment."
            )
        other_pk = self.kwargs.get(self.other_pk_kwarg)
        other_object = self.other_model.objects.get(
            pk=other_pk
        )
        manager = getattr(other_object, self.other_field_name)
        manager.add(attachment)
        other_object.save()

    def get_success_url(self):
        return reverse(
            "proposals:attachments",
            kwargs={
                "pk": self.kwargs.get(self.other_pk_kwarg),
            }
        )
