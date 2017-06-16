# -*- encoding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from core.forms import ConditionalModelForm
from core.utils import YES_NO
from .models import Session, Task


class TaskStartForm(ConditionalModelForm):
    is_copy = forms.BooleanField(
        label=_('Is deze sessie een kopie van een voorgaande sessie?'),
        help_text=_(u'Na het kopiëren zijn alle velden bewerkbaar.'),
        widget=forms.RadioSelect(choices=YES_NO),
        initial=False,
        required=False)
    parent_session = forms.ModelChoiceField(
        label=_(u'Te kopiëren sessie'),
        queryset=Session.objects.all(),
        required=False)

    class Meta:
        model = Session
        fields = [
            'setting', 'setting_details', 'supervision',
            'tasks_number',
        ]
        widgets = {
            'setting': forms.CheckboxSelectMultiple(),
            'supervision': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - The field tasks_number is not required by default (only if is_copy is set to False)
        - Only allow to choose earlier Sessions
        - Remove option to copy altogether from first Session
        - Don't ask the supervision question when there are only adult AgeGroups in this Study
        """
        self.study = kwargs.pop('study', None)

        super(TaskStartForm, self).__init__(*args, **kwargs)
        self.fields['tasks_number'].required = False
        self.fields['parent_session'].queryset = Session.objects.filter(study=self.instance.study.pk,
                                                                        order__lt=self.instance.order)

        if self.instance.order == 1:
            del self.fields['is_copy']
            del self.fields['parent_session']

        if not self.study.has_children():
            del self.fields['supervision']

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details or supervision has been checked, make sure the details are filled
        - If is_copy is True, parent_session is required
        - If is_copy is False, tasks_number is required
        """
        cleaned_data = super(TaskStartForm, self).clean()

        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        if self.study.has_children():
            self.check_dependency_multiple(cleaned_data, 'setting', 'needs_supervision', 'supervision')

        self.check_dependency(cleaned_data, 'is_copy', 'parent_session')
        if not cleaned_data.get('is_copy') and not cleaned_data.get('tasks_number'):
            self.add_error('tasks_number', forms.ValidationError(_('Dit veld is verplicht.'), code='required'))


class TaskForm(ConditionalModelForm):
    class Meta:
        model = Task
        fields = [
            'name', 'description', 'duration',
            'registrations', 'registrations_details',
            'registration_kinds', 'registration_kinds_details',
            'feedback', 'feedback_details',
        ]
        widgets = {
            'registrations': forms.CheckboxSelectMultiple(),
            'registration_kinds': forms.CheckboxSelectMultiple(),
            'feedback': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['duration'].label = mark_safe(self.fields['duration'].label)

    def clean(self):
        """
        Check for conditional requirements:
        - Check if feedback has been filled out
        - If a registration which needs a kind has been checked, make sure the kind is selected
        - If a registration which needs details has been checked, make sure the details are filled
        - If a registration_kind which needs details has been checked, make sure the details are filled
        - If feedback is set to yes, make sure feedback_details has been filled out
        """
        cleaned_data = super(TaskForm, self).clean()

        self.check_empty(cleaned_data, 'feedback')
        self.check_dependency_multiple(cleaned_data, 'registrations', 'needs_kind', 'registration_kinds')
        self.check_dependency_multiple(cleaned_data, 'registrations', 'needs_details', 'registrations_details')
        self.check_dependency_multiple(cleaned_data, 'registration_kinds', 'needs_details', 'registration_kinds_details')
        self.check_dependency(cleaned_data, 'feedback', 'feedback_details')


class TaskEndForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['tasks_duration']

    def __init__(self, *args, **kwargs):
        """
        - Set the tasks_duration label
        - Set the tasks_duration as required
        """
        super(TaskEndForm, self).__init__(*args, **kwargs)

        tasks_duration = self.fields['tasks_duration']
        tasks_duration.required = True
        label = tasks_duration.label % self.instance.net_duration()
        tasks_duration.label = mark_safe(label)

    def clean_tasks_duration(self):
        """
        Check that the net duration is at least equal to the gross duration
        """
        tasks_duration = self.cleaned_data.get('tasks_duration')

        if tasks_duration < self.instance.net_duration():
            raise forms.ValidationError(_('Totale sessieduur moet minstens gelijk zijn aan netto sessieduur.'), code='comparison')

        return tasks_duration
