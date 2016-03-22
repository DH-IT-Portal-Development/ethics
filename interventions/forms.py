from django import forms

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Intervention


class InterventionForm(ConditionalModelForm):
    class Meta:
        model = Intervention
        fields = ['description', 'has_drawbacks', 'has_drawbacks_details']
        widgets = {
            'has_drawbacks': forms.RadioSelect(choices=YES_NO),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If has_drawbacks is True, has_drawbacks_details is required
        """
        cleaned_data = super(InterventionForm, self).clean()

        self.check_dependency(cleaned_data, 'has_drawbacks', 'has_drawbacks_details')