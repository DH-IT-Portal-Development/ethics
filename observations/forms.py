from django import forms

from extra_views import InlineFormSet

from core.utils import YES_NO
from .models import Observation, Location


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ['days', 'mean_hours',
                  'is_anonymous', 'is_test']
        widgets = {
            'mean_hours': forms.NumberInput(attrs={'step': 0.25}),
            'is_anonymous': forms.RadioSelect(choices=YES_NO),
            'is_test': forms.RadioSelect(choices=YES_NO),
        }


class LocationsInline(InlineFormSet):
    """Creates an InlineFormSet for Locations"""
    model = Location
    fields = ['name', 'registration']
    can_delete = True
    extra = 1
