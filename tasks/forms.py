# -*- encoding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from main.forms import ConditionalModelForm, SoftValidationMixin
from main.utils import YES_NO
from tasks.models import Study
from .models import Session, Task


from django.utils.safestring import mark_safe, SafeString
from django.utils.functional import lazy

from cdh.core.forms import (
    BootstrapRadioSelect,
    BootstrapCheckboxSelectMultiple,
)

mark_safe_lazy = lazy(mark_safe, SafeString)


class SessionUpdateForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Session
        fields = [
            "repeats",
            "setting",
            "setting_details",
            "supervision",
            "leader_has_coc",
        ]
        widgets = {
            "setting": BootstrapCheckboxSelectMultiple(),
            "supervision": BootstrapRadioSelect(choices=YES_NO),
            "leader_has_coc": BootstrapRadioSelect(choices=YES_NO),
        }

    _soft_validation_fields = [
        "repeats",
        "setting",
        "setting_details",
        "supervision",
        "leader_has_coc",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Only allow to choose earlier Sessions
        - Remove option to copy altogether from first Session
        - Don't ask the supervision question when there are only adult AgeGroups in this Study
        """
        self.study = kwargs.pop("study", None)

        super(SessionUpdateForm, self).__init__(*args, **kwargs)

        # TODO: add warning
        if not self.study.has_children():
            del self.fields["supervision"]
            del self.fields["leader_has_coc"]

    def clean(self):
        """
        Check for conditional requirements:
        - If a setting which needs details or supervision has been checked, make sure the details are filled
        - If is_copy is True, parent_session is required
        """
        cleaned_data = super(SessionUpdateForm, self).clean()

        self.mark_soft_required(cleaned_data, "setting")

        self.check_dependency_multiple(
            cleaned_data, "setting", "needs_details", "setting_details"
        )
        if self.study.has_children():
            self.check_dependency_multiple(
                cleaned_data, "setting", "needs_supervision", "supervision"
            )
            self.check_dependency(
                cleaned_data, "supervision", "leader_has_coc", f1_value=False
            )


class TaskForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "repeats",
            "duration",
            "registrations",
            "registrations_details",
            "registration_kinds",
            "registration_kinds_details",
            "feedback",
            "feedback_details",
        ]
        labels = {
            "duration": mark_safe_lazy(
                _(
                    "Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, \
dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak \
(exclusief instructie maar inclusief oefensessie)? \
Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), \
geef dan <strong>het redelijkerwijs te verwachten maximum op</strong>."
                )
            ),
        }
        widgets = {
            "registrations": BootstrapCheckboxSelectMultiple(),
            "registration_kinds": BootstrapCheckboxSelectMultiple(),
            "feedback": BootstrapRadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

    def get_soft_validation_fields(self):
        # All fields should be validated softly
        return self.fields.keys()

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

        self.mark_soft_required(
            cleaned_data,
            "name",
            "description",
            "duration",
            #'registrations',
        )

        self.check_empty(cleaned_data, "feedback")
        self.check_dependency_multiple(
            cleaned_data, "registrations", "needs_kind", "registration_kinds"
        )
        self.check_dependency_multiple(
            cleaned_data, "registrations", "needs_details", "registrations_details"
        )
        self.check_dependency_multiple(
            cleaned_data,
            "registration_kinds",
            "needs_details",
            "registration_kinds_details",
        )
        self.check_dependency(cleaned_data, "feedback", "feedback_details")


class SessionEndForm(SoftValidationMixin, forms.ModelForm):
    class Meta:
        model = Session
        fields = ["tasks_duration"]

    _soft_validation_fields = [
        "tasks_duration",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Set the tasks_duration label
        - Set the tasks_duration as required
        """
        super(SessionEndForm, self).__init__(*args, **kwargs)

        tasks_duration = self.fields["tasks_duration"]
        label = tasks_duration.label % self.instance.net_duration()
        tasks_duration.label = mark_safe(label)

    def is_initial_visit(self) -> bool:
        return True

    def clean(self):
        cleaned_data = super(SessionEndForm, self).clean()

        self.mark_soft_required(cleaned_data, "tasks_duration")

        return cleaned_data

    def clean_tasks_duration(self):
        """
        Check that the net duration is at least equal to the gross duration
        """
        tasks_duration = self.cleaned_data.get("tasks_duration")

        if tasks_duration and tasks_duration < self.instance.net_duration():
            raise forms.ValidationError(
                _("Totale sessieduur moet minstens gelijk zijn aan netto sessieduur."),
                code="comparison",
            )

        return tasks_duration


class SessionOverviewForm(SoftValidationMixin, ModelForm):
    """This is form is mostly used to make the navigation work on
    SessionOverview and SessionStart. However, it is also use to validate
    that if study.has_session, it also contains sessions."""

    class Meta:
        model = Study
        fields = []

    def get_soft_validation_fields(self):
        return self.errors

    def clean(self):
        cleaned_data = super(SessionOverviewForm, self).clean()

        if self.instance.has_no_sessions():
            self.add_error(
                None,
                _(
                    "Je hebt aangegeven dat traject {} sessie's en taken bevat, maar er zijn nog geen sessie's aangemaakt."
                ).format(self.instance.order),
            )

        return cleaned_data
