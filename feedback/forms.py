from django import forms

from cdh.core.forms import TemplatedModelForm
from .models import Feedback


class FeedbackForm(TemplatedModelForm):
    show_help_column = False

    class Meta:
        model = Feedback
        fields = ['url', 'comment']
        widgets = {
            'url': forms.HiddenInput(),
        }
