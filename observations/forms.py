# -*- encoding: utf-8 -*-

from django import forms

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Observation


class ObservationForm(ConditionalModelForm):
    class Meta:
        model = Observation
        fields = [
            'setting', 'setting_details', 'supervision', 'leader_has_coc',
            'days', 'mean_hours',
            'is_anonymous', 'is_in_target_group',
            'is_nonpublic_space', 'has_advanced_consent',
            'needs_approval', 'approval_institution', 'approval_document',
            'registrations', 'registrations_details',
        ]
        widgets = {
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
            'leader_has_coc': forms.RadioSelect(choices=YES_NO),
            'is_anonymous': forms.RadioSelect(choices=YES_NO),
            'is_in_target_group': forms.RadioSelect(choices=YES_NO),
            'is_nonpublic_space': forms.RadioSelect(choices=YES_NO),
            'has_advanced_consent': forms.RadioSelect(choices=YES_NO),
            'needs_approval': forms.RadioSelect(choices=YES_NO),
            'registrations': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Don't ask the supervision question when there are only adult AgeGroups in this Study
        """
        self.study = kwargs.pop('study', None)

        super(ObservationForm, self).__init__(*args, **kwargs)

        if not self.study.has_children():
            del self.fields['supervision']
            del self.fields['leader_has_coc']

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details or supervision has been checked, make sure the details are filled
        - If the Observation needs_approval, check if approval_institution/approval_document are provided
        - If a registration which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(ObservationForm, self).clean()

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        if self.study.has_children():
            self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
            self.check_dependency(cleaned_data, 'supervision', 'leader_has_coc', f1_value=False)
        self.check_dependency(cleaned_data, 'needs_approval', 'approval_institution')
        self.check_dependency_multiple(cleaned_data, 'registrations', 'needs_details', 'registrations_details')

        # Approval document only needs to be added for non-practice Proposals
        if not self.study.proposal.is_practice():
            self.check_dependency(cleaned_data, 'needs_approval', 'approval_document')


class ObservationUpdateAttachmentsForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = [
            'approval_document',
        ]
