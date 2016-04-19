# -*- encoding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from core.forms import ConditionalModelForm
from core.utils import YES_NO, YES_NO_DOUBT
from .models import Study
from .utils import check_necessity_required


class StudyForm(ConditionalModelForm):
    class Meta:
        model = Study
        fields = ['name', 'age_groups', 'legally_incapable',
                  'has_traits', 'traits', 'traits_details',
                  'necessity', 'necessity_reason',
                  'recruitment', 'recruitment_details',
                  'setting', 'setting_details', 'supervision',
                  'compensation', 'compensation_details',
                  'passive_consent']
        widgets = {
            'age_groups': forms.CheckboxSelectMultiple(),
            'legally_incapable': forms.RadioSelect(choices=YES_NO),
            'has_traits': forms.RadioSelect(choices=YES_NO),
            'traits': forms.CheckboxSelectMultiple(),
            'necessity': forms.RadioSelect(choices=YES_NO_DOUBT),
            'recruitment': forms.CheckboxSelectMultiple(),
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
            'compensation': forms.RadioSelect(),
            'passive_consent': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Allow legally_incapable to have HTML in its label
        - Remove empty label from setting/compensation field
        - Set the Proposal for later reference in the clean method
        """
        self.proposal = kwargs.pop('proposal', None)

        super(StudyForm, self).__init__(*args, **kwargs)
        self.fields['legally_incapable'].label = mark_safe(self.fields['legally_incapable'].label)
        self.fields['setting'].empty_label = None
        self.fields['compensation'].empty_label = None

    def clean(self):
        """
        Check for conditional requirements:
        - Check whether necessity_reason was required and if so, if it has been filled out
        - If has_traits is checked, make sure there is at least one trait selected
        - If a trait which needs details has been checked, make sure the details are filled
        - If a setting which needs details has been checked, make sure the details are filled
        - If a compensation which needs details has been checked, make sure the details are filled
        - If a recruitment which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(StudyForm, self).clean()

        self.necessity_required(cleaned_data)
        self.check_dependency(cleaned_data, 'has_traits', 'traits', _('U dient minimaal een bijzonder kenmerk te selecteren.'))
        self.check_dependency_multiple(cleaned_data, 'traits', 'needs_details', 'traits_details')
        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        # TODO: this doesn't work as supervision is a boolean value
        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
        self.check_dependency_singular(cleaned_data, 'compensation', 'needs_details', 'compensation_details')
        self.check_dependency_multiple(cleaned_data, 'recruitment', 'needs_details', 'recruitment_details')

    def necessity_required(self, cleaned_data):
        """
        Check whether necessity_reason was required and if so, if it has been filled out.
        """
        age_groups = cleaned_data['age_groups'].values_list('id', flat=True) if 'age_groups' in cleaned_data else []
        if check_necessity_required(self.proposal,
                                    age_groups,
                                    cleaned_data['has_traits'],
                                    cleaned_data['legally_incapable']):
            if not cleaned_data['necessity_reason']:
                error = forms.ValidationError(_('Dit veld is verplicht'), code='required')
                self.add_error('necessity_reason', error)


class StudyDesignForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['has_observation', 'has_intervention', 'has_sessions']

    def clean(self):
        """
        Check for conditional requirements:
        - at least one of the fields has to be checked
        """
        cleaned_data = super(StudyDesignForm, self).clean()
        if not (cleaned_data.get('has_observation') or cleaned_data.get('has_intervention') or cleaned_data.get('has_sessions')):
            msg = _(u'U dient minstens één van de opties te selecteren')
            self.add_error('has_sessions', forms.ValidationError(msg, code='required'))


class StudyConsentForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['informed_consent', 'briefing']


class SessionStartForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['sessions_number']

    def __init__(self, *args, **kwargs):
        """Set the sessions_number field as required"""
        super(SessionStartForm, self).__init__(*args, **kwargs)
        self.fields['sessions_number'].required = True


class SessionEndForm(ConditionalModelForm):
    class Meta:
        model = Study
        fields = ['stressful', 'stressful_details',
                  'risk', 'risk_details']
        widgets = {
            'stressful': forms.RadioSelect(choices=YES_NO_DOUBT),
            'risk': forms.RadioSelect(choices=YES_NO_DOUBT),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set stressful and risk as required and mark_safe the labels
        """
        super(SessionEndForm, self).__init__(*args, **kwargs)

        self.fields['stressful'].required = True
        self.fields['risk'].required = True
        self.fields['stressful'].label = mark_safe(self.fields['stressful'].label)
        self.fields['risk'].label = mark_safe(self.fields['risk'].label)

    def clean(self):
        """
        Check for conditional requirements:
        - Check that the net duration is at least equal to the gross duration
        - If stressful is set to yes, make sure stressful_details has been filled out
        - If risk is set to yes, make sure risk_details has been filled out
        """
        cleaned_data = super(SessionEndForm, self).clean()

        self.check_dependency(cleaned_data, 'stressful', 'stressful_details')
        self.check_dependency(cleaned_data, 'risk', 'risk_details')
