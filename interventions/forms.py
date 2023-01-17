from django import forms

from cdh.core.forms import BootstrapCheckboxSelectMultiple, BootstrapRadioSelect
from main.forms import ConditionalModelForm, SoftValidationMixin
from main.utils import YES_NO
from .models import Intervention


class InterventionForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Intervention
        fields = [
            'setting', 'setting_details', 'supervision', 'leader_has_coc',
            'period', 'multiple_sessions', 'session_frequency', 'duration',
            'experimenter', 'description',
            'has_controls', 'controls_description',
            'measurement', 'extra_task'
        ]
        widgets = {
            'setting':           BootstrapCheckboxSelectMultiple(),
            'supervision':       BootstrapRadioSelect(choices=YES_NO),
            'multiple_sessions': BootstrapRadioSelect(choices=YES_NO),
            'leader_has_coc':    BootstrapRadioSelect(choices=YES_NO),
            'has_controls':      BootstrapRadioSelect(choices=YES_NO),
            'extra_task':        BootstrapRadioSelect(choices=YES_NO),
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
            del self.fields['leader_has_coc']

    def get_soft_validation_fields(self):
        # We want soft validation on all fields
        return self.fields.keys()

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details or supervision has been checked, make sure the details are filled
        - If has_controls is True, controls_description is required
        - If multiple_sessions is True, session_frequency is required
        """
        cleaned_data = super(InterventionForm, self).clean()

        self.mark_soft_required(
            cleaned_data,
            'setting',
            'period',
            'experimenter',
            'description',
            'measurement',
        )

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details',
                                       'setting_details')
        if self.study.has_children():
            self.check_dependency_multiple(cleaned_data, 'setting',
                                           'needs_supervision', 'supervision')
            self.check_dependency(cleaned_data, 'supervision', 'leader_has_coc',
                                  f1_value=False)
        self.check_dependency(cleaned_data, 'has_controls',
                              'controls_description')
        self.check_dependency(cleaned_data, 'multiple_sessions',
                              'session_frequency')
