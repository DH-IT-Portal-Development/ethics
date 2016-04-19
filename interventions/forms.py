from django import forms

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Intervention


class InterventionForm(ConditionalModelForm):
    class Meta:
        model = Intervention
        fields = [
            'setting', 'setting_details', 'supervision',
            'description',
            'has_drawbacks', 'has_drawbacks_details',
            'is_supervised']
        widgets = {
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
            'has_drawbacks': forms.RadioSelect(choices=YES_NO),
            'is_supervised': forms.RadioSelect(choices=YES_NO),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details has been checked, make sure the details are filled
        - If has_drawbacks is True, has_drawbacks_details is required
        """
        cleaned_data = super(InterventionForm, self).clean()

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        # TODO: this doesn't work as supervision is a boolean value
        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
        self.check_dependency(cleaned_data, 'has_drawbacks', 'has_drawbacks_details')
