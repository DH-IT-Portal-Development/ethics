from django import forms

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Intervention


class InterventionForm(ConditionalModelForm):
    class Meta:
        model = Intervention
        fields = [
            'setting', 'setting_details', 'supervision',
            'period', 'amount_per_week', 'duration',
            'experimenter', 'description',
            'has_controls', 'controls_description',
            'measurement',
        ]
        widgets = {
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
            'has_controls': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Don't ask the supervision question when there are only adult AgeGroups in this Study
        """
        self.study = kwargs.pop('study', None)

        super(InterventionForm, self).__init__(*args, **kwargs)

        if not self.study.has_children():
            del self.fields['supervision']

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details or supervision has been checked, make sure the details are filled
        - If has_controls is True, controls_description is required
        """
        cleaned_data = super(InterventionForm, self).clean()

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        if self.study.has_children():
            self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
        self.check_dependency(cleaned_data, 'has_controls', 'controls_description')
