from django import forms

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Intervention


class InterventionForm(ConditionalModelForm):
    class Meta:
        model = Intervention
        fields = [
            'setting', 'setting_details', 'supervision',
            'period', 'amount_per_week', 'duration', 'measurement',
            'experimenter', 'description',
            'has_controls', 'controls_description',
            ]
        widgets = {
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
            'has_controls': forms.RadioSelect(choices=YES_NO),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details has been checked, make sure the details are filled
        - If has_controls is True, controls_description is required
        """
        cleaned_data = super(InterventionForm, self).clean()

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
        self.check_dependency(cleaned_data, 'has_controls', 'controls_description')
