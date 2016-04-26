from django import forms
from django.utils.translation import ugettext as _

from core.forms import ConditionalModelForm
from core.utils import YES_NO, get_users_as_list
from .models import Intervention


class InterventionForm(ConditionalModelForm):
    has_observation = forms.BooleanField(label='')
    has_sessions = forms.BooleanField(label='')

    class Meta:
        model = Intervention
        fields = [
            'setting', 'setting_details', 'supervision',
            'number', 'duration', 'experimenter', 'description',
            'has_controls', 'has_controls_details',
            'has_recording', 'recording_same_experimenter', 'recording_experimenter',
            ]
        widgets = {
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
            'description': forms.Textarea(attrs={'cols': 50}),
            'has_controls': forms.RadioSelect(choices=YES_NO),
            'has_recording': forms.RadioSelect(choices=YES_NO),
            'recording_same_experimenter': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the choices for experimenters to the applicants of the proposal
        """
        self.proposal = kwargs.pop('proposal', None)
        super(InterventionForm, self).__init__(*args, **kwargs)
        applicants = get_users_as_list(self.proposal.applicants.all())
        self.fields['experimenter'].choices = applicants
        self.fields['recording_experimenter'].choices = applicants

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details has been checked, make sure the details are filled
        - If has_controls is True, has_controls_details is required
        - If has_recording is True and recording_same_experimenter is set to False check:
        -- Whether the recording_experimenter has been set.
        -- Whether the recording_experimenter is someone else than the experimenter.
        """
        cleaned_data = super(InterventionForm, self).clean()

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        # TODO: this doesn't work as supervision is a boolean value
        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')
        self.check_dependency(cleaned_data, 'has_controls', 'has_controls_details')

        if cleaned_data.get('has_recording') and not cleaned_data.get('recording_same_experimenter'):
            if not cleaned_data.get('recording_experimenter'):
                self.add_error('recording_experimenter', forms.ValidationError(_('Dit veld is verplicht.'), code='required'))
            if cleaned_data.get('experimenter') == cleaned_data.get('recording_experimenter'):
                self.add_error('recording_experimenter', forms.ValidationError(_('U moet een andere uitvoerende selecteren.'), code='required'))
