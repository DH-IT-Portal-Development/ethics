from django import forms

from extra_views import InlineFormSet

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Observation, Location


class ObservationForm(ConditionalModelForm):
    class Meta:
        model = Observation
        fields = [
            'days', 'mean_hours',
            'is_anonymous', 'is_in_target_group',
            'is_nonpublic_space', 'has_advanced_consent',
            'needs_approval', 'approval_institution', 'approval_document']
        widgets = {
            'mean_hours': forms.NumberInput(attrs={'step': 0.25}),
            'is_anonymous': forms.RadioSelect(choices=YES_NO),
            'is_in_target_group': forms.RadioSelect(choices=YES_NO),
            'is_nonpublic_space': forms.RadioSelect(choices=YES_NO),
            'has_advanced_consent': forms.RadioSelect(choices=YES_NO),
            'needs_approval': forms.RadioSelect(choices=YES_NO),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If the Observation needs_approval, check if approval_institution is provided
        """
        cleaned_data = super(ObservationForm, self).clean()

        self.check_dependency(cleaned_data, 'needs_approval', 'approval_institution')


class LocationsInline(InlineFormSet):
    """Creates an InlineFormSet for Locations"""
    model = Location
    fields = ['name', 'registrations', 'registrations_details']
    can_delete = True
    extra = 1
