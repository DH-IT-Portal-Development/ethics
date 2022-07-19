# -*- encoding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe

from cdh.core.forms import BootstrapCheckboxSelectMultiple, BootstrapRadioSelect
from main.forms import ConditionalModelForm, SoftValidationMixin
from main.utils import YES_NO
from .models import Observation


class ObservationForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Observation
        fields = [
            'setting', 'setting_details', 'supervision', 'leader_has_coc',
            'details_who', 'details_why', 'details_frequency',
            'is_anonymous', 'is_anonymous_details', 'is_in_target_group',
            'is_in_target_group_details', 'is_nonpublic_space', 'is_nonpublic_space_details',
            'has_advanced_consent', 'has_advanced_consent_details',
            'needs_approval', 'approval_institution',
            'registrations', 'registrations_details',
        ]
        widgets = {
            'setting': BootstrapCheckboxSelectMultiple(),
            'supervision': BootstrapRadioSelect(choices=YES_NO),
            'leader_has_coc': BootstrapRadioSelect(choices=YES_NO),
            'is_anonymous': BootstrapRadioSelect(choices=YES_NO),
            'is_in_target_group': BootstrapRadioSelect(choices=YES_NO),
            'is_nonpublic_space': BootstrapRadioSelect(choices=YES_NO),
            'has_advanced_consent': BootstrapRadioSelect(choices=YES_NO),
            'needs_approval': BootstrapRadioSelect(choices=YES_NO),
            'registrations': BootstrapCheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Don't ask the supervision question when there are only adult AgeGroups in this Study
        """
        self.study = kwargs.pop('study', None)

        super(ObservationForm, self).__init__(*args, **kwargs)

        self.fields['details_who'].label = mark_safe(self.fields['details_who'].label)
        self.fields['details_why'].label = mark_safe(self.fields['details_why'].label)
        self.fields['details_frequency'].label = mark_safe(self.fields['details_frequency'].label)

        if not self.study.has_children():
            del self.fields['supervision']
            del self.fields['leader_has_coc']

        self._bound_fields_cache = {}

    def get_soft_validation_fields(self):
        # We want soft validation of all fields
        return self.fields.keys()

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details or supervision has been checked, make sure the details are filled
        - If a registration which needs details has been checked, make sure the details are filled
        - For all default anonymity questions, if true, the appropiate explain fields need to be filled
        """
        cleaned_data = super(ObservationForm, self).clean()

        self.mark_soft_required(
            cleaned_data,
            'setting',
            'details_who',
            'details_why',
            'details_frequency',
        )

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        if self.study.has_children():
            self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
            self.check_dependency(cleaned_data, 'supervision', 'leader_has_coc', f1_value=False)
        self.check_dependency(cleaned_data, 'needs_approval', 'approval_institution')
        self.check_dependency_multiple(cleaned_data, 'registrations', 'needs_details', 'registrations_details')

        self.check_dependency(cleaned_data, 'is_anonymous', 'is_anonymous_details')
        self.check_dependency(cleaned_data, 'is_in_target_group', 'is_in_target_group_details')
        self.check_dependency(cleaned_data, 'is_nonpublic_space', 'is_nonpublic_space_details')


class ObservationUpdateAttachmentsForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = [
            'approval_document',
        ]
