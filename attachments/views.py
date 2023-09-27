from django.views import generic
from django.forms import forms, ModelForm
from django.core.exceptions import ImproperlyConfigured
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

    pass

class AttachmentCreateView(generic.CreateView):
    """Generic create view to create a new attachment. Both other_model and
    template_name should be provided externally, either through the URL
    definition or through subclassing."""

    model = Attachment
    form_class = AttachmentForm
    template_name = None

    other_model = None
    other_field_name = "attachments"
    other_pk_kwarg = "other_pk"

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def form_valid(self, form):
        self.attach(form.instance)
        return super().form_valid()

    def attach(self, attachment):
        if self.other_model is None:
            raise ImproperlyConfigured(
                "Please provide an other_model as a target for "
                "this attachment."
            )
        other_pk = self.kwargs.get(other_pk_kwarg)
        other_object = self.other_model.objects.get(
            pk=other_pk
        )
        manager = getattr(other_object, self.other_field_name)
        manager.add(attachment)
        other_object.save()
