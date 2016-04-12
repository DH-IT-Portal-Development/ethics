# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

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


class LocationInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """
        - There should be at least one Location
        - If a Registration which needs details has been checked, make sure the details are filled
        """
        count = 0
        for form in self.forms:
            cleaned_data = form.cleaned_data
            if cleaned_data and not cleaned_data.get('DELETE', False):
                count += 1

                if cleaned_data.get('registrations'):
                    for registration in cleaned_data.get('registrations'):
                        if registration.needs_details and not cleaned_data.get('registrations_details'):
                            error_message = _('Dit veld is verplicht')
                            form.add_error('registrations_details', forms.ValidationError(error_message, code='required'))
                            break

        if count == 0:
            first_form = self.forms[0]
            error = forms.ValidationError(_(u'U dient op zijn minst één locatie aan te geven.'), code='required')
            if first_form.is_valid():
                first_form.add_error('name', error)
            else:
                # TODO: find a way to show this error in the template
                raise error


class LocationsInline(InlineFormSet):
    """Creates an InlineFormSet for Locations"""
    model = Location
    fields = ['name', 'registrations', 'registrations_details']
    can_delete = True
    extra = 1
    formset_class = LocationInlineFormSet
