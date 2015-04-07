from django import forms
from django.utils.safestring import mark_safe

from .models import Proposal, Wmo, Study, Task

yes_no = [(True, "ja"), (False, "nee")]
yes_no_doubt = [(True, "ja"), (False, "nee"), (None, "twijfel")]

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['relation', 'supervisor_email', 'other_applicants', 'applicants', 'title', 'tech_summary', 'longitudinal']
        widgets = {
            'relation': forms.RadioSelect(),
            'other_applicants': forms.RadioSelect(choices=yes_no),
            'longitudinal': forms.RadioSelect(choices=yes_no),
        }

    def __init__(self, *args, **kwargs):
        """Remove empty label from relation field"""
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['relation'].empty_label = None

    def clean(self):
        """
        Check for conditional requirements: 
        - If relation needs supervisor, make sure supervisor_email is set
        - TODO: If other_applicants is checked, make sure applicants are set
        """
        cleaned_data = super(ProposalForm, self).clean()
        relation = cleaned_data.get('relation')
        supervisor_email = cleaned_data.get('supervisor_email')

        if relation and relation.needs_supervisor and not supervisor_email:
            self.add_error('supervisor_email', forms.ValidationError('U dient een eindverantwoordelijke op te geven.', code='required'))


class WmoForm(forms.ModelForm):
    class Meta:
        model = Wmo
        fields = ['metc', 'metc_institution', 'is_medical', 'is_behavioristic', 'metc_application', 'metc_decision', 'metc_decision_pdf']
        widgets = {
            'metc': forms.RadioSelect(choices=yes_no_doubt),
            'is_medical': forms.RadioSelect(choices=yes_no_doubt),
            'is_behavioristic': forms.RadioSelect(choices=yes_no_doubt),
            'metc_application': forms.RadioSelect(choices=yes_no),
            'metc_decision': forms.RadioSelect(choices=yes_no),
        }
    def clean(self):
        """
        Check for conditional requirements: 
        - If metc is checked, make sure institution is set
        """
        cleaned_data = super(WmoForm, self).clean()
        metc = cleaned_data.get('metc')
        metc_institution = cleaned_data.get('metc_institution')

        if metc and not metc_institution:
            self.add_error('metc_institution', forms.ValidationError('U dient een instelling op te geven.', code='required'))

class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['age_groups', 'has_traits', 'traits', 'traits_details', 'necessity', 'necessity_reason', 'setting', 'setting_details', \
            'risk_physical', 'risk_psychological', 'compensation', 'compensation_details', 'recruitment', 'recruitment_details']
        widgets = {
            'age_groups': forms.CheckboxSelectMultiple(),
            'has_traits': forms.RadioSelect(choices=yes_no),
            'traits': forms.CheckboxSelectMultiple(),
            'necessity': forms.RadioSelect(choices=yes_no_doubt),
            'risk_physical': forms.RadioSelect(choices=yes_no_doubt),
            'setting': forms.RadioSelect(),
            'risk_psychological': forms.RadioSelect(choices=yes_no_doubt),
            'compensation': forms.RadioSelect(),
            'recruitment': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        """Remove empty label from setting field"""
        super(StudyForm, self).__init__(*args, **kwargs)
        self.fields['setting'].empty_label = None
        self.fields['compensation'].empty_label = None

class TaskStartForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['tasks_number']

    def __init__(self, *args, **kwargs):
        """Set the tasks_number field as required"""
        super(TaskStartForm, self).__init__(*args, **kwargs)
        self.fields['tasks_number'].required = True

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'duration', 'actions', 'actions_details', 'registrations', 'registrations_details', \
            'feedback', 'feedback_details', 'stressful']
        widgets = {
            'procedure': forms.RadioSelect(choices=yes_no_doubt),
            'actions': forms.CheckboxSelectMultiple(),
            'registrations': forms.CheckboxSelectMultiple(),
            'feedback': forms.RadioSelect(choices=yes_no),
            'stressful': forms.RadioSelect(choices=yes_no_doubt),
        }

class TaskEndForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['tasks_duration', 'tasks_stressful']
        widgets = {
            'tasks_stressful': forms.RadioSelect(choices=yes_no_doubt),
        }

    def __init__(self, *args, **kwargs):
        """Set the tasks_duration and tasks_stressful fields as required"""
        super(TaskEndForm, self).__init__(*args, **kwargs)
        self.fields['tasks_duration'].required = True
        self.fields['tasks_duration'].label = mark_safe(self.fields['tasks_duration'].label.format(**self.instance.gross_duration()))
        self.fields['tasks_stressful'].required = True

class UploadConsentForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['informed_consent_pdf']

    def __init__(self, *args, **kwargs):
        super(UploadConsentForm, self).__init__(*args, **kwargs)
        self.fields['informed_consent_pdf'].required = True

class ProposalSubmitForm(forms.ModelForm):
    class Meta:
        model = Proposal
