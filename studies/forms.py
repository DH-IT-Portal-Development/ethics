# -*- encoding: utf-8 -*-

from django import forms
from django.utils.functional import lazy
from django.utils.safestring import mark_safe, SafeString
from django.utils.translation import gettext_lazy as _

from main.forms import ConditionalModelForm, SoftValidationMixin
from main.models import YesNoDoubt
from main.utils import YES_NO
from .models import AgeGroup, Documents, Study
from .utils import check_necessity_required

from cdh.core.forms import (
    DateField,
    BootstrapRadioSelect,
    BootstrapCheckboxSelectMultiple,
    BootstrapSelect,
    SearchableSelectWidget,
    DateInput,
    SplitDateTimeWidget,
    BootstrapSplitDateTimeWidget,
    TemplatedForm,
    TemplatedModelForm,
)


class StudyForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Study
        fields = [
            "age_groups",
            "legally_incapable",
            "legally_incapable_details",
            "has_special_details",
            "special_details",
            "traits",
            "traits_details",
            "necessity",
            "necessity_reason",
            "recruitment",
            "recruitment_details",
            "compensation",
            "compensation_details",
            "hierarchy",
            "hierarchy_details",
        ]
        widgets = {
            "age_groups": BootstrapCheckboxSelectMultiple(),
            "legally_incapable": BootstrapRadioSelect(choices=YES_NO),
            "has_special_details": BootstrapRadioSelect(choices=YES_NO),
            "hierarchy": BootstrapRadioSelect(choices=YES_NO),
            "special_details": BootstrapCheckboxSelectMultiple(),
            "traits": BootstrapCheckboxSelectMultiple(),
            "necessity": BootstrapRadioSelect(),
            "recruitment": BootstrapCheckboxSelectMultiple(),
            "compensation": BootstrapRadioSelect(),
        }
        mark_safe_lazy = lazy(mark_safe, SafeString)
        labels = {
            "legally_incapable": mark_safe_lazy(
                _(
                    "Maakt jouw onderzoek gebruik van "
                    "wils<u>on</u>bekwame ("
                    "volwassen) deelnemers?"
                )
            )
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Proposal for later reference in the clean method
        - Allow legally_incapable to have HTML in its label
        - Remove the empty label for compensation/necessity
        - Reset the choices for necessity
        """
        self._soft_validation_fields = self._meta.fields
        self.proposal = kwargs.pop("proposal", None)

        super(StudyForm, self).__init__(*args, **kwargs)
        self.fields["compensation"].empty_label = None
        self.fields["necessity"].empty_label = None
        self.fields["necessity"].choices = YesNoDoubt.choices

        self.fields["age_groups"].queryset = AgeGroup.objects.filter(is_active=True)

    def clean(self):
        """
        Check for conditional requirements:
        - Check that a compensation was selected
        - Check whether necessity was required
        - Check that legally_incapable has a value
        - If legally_incapable is set, make sure the details are filled
        - If a trait which needs details has been checked, make sure the details are filled
        - If a compensation which needs details has been checked, make sure the details are filled
        - If a recruitment which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(StudyForm, self).clean()

        self.mark_soft_required(cleaned_data, "compensation", "recruitment")

        self.necessity_required(cleaned_data)
        self.check_dependency(
            cleaned_data, "legally_incapable", "legally_incapable_details"
        )
        self.check_dependency_multiple(
            cleaned_data,
            "special_details",
            "medical_traits",
            "traits",
            _("Je dient minimaal een bijzonder kenmerk te selecteren."),
        )
        self.check_dependency(
            cleaned_data,
            "has_special_details",
            "special_details",
            True,
            _("Je dient minimaal één type gegevens te selecteren."),
        )
        self.check_dependency_multiple(
            cleaned_data, "traits", "needs_details", "traits_details"
        )
        self.check_dependency_singular(
            cleaned_data, "compensation", "needs_details", "compensation_details"
        )
        self.check_dependency_multiple(
            cleaned_data, "recruitment", "needs_details", "recruitment_details"
        )
        self.check_dependency(
            cleaned_data,
            "hierarchy",
            "hierarchy_details",
            True,
            _("Leg uit wat de hiërarchische relatie is."),
        )

    def necessity_required(self, cleaned_data):
        """
        Check whether necessity_reason was required and if so, if it has been filled out.
        """
        age_groups = (
            cleaned_data["age_groups"].values_list("id", flat=True)
            if "age_groups" in cleaned_data
            else []
        )
        legally_incapable = bool(cleaned_data["legally_incapable"])
        if check_necessity_required(self.proposal, age_groups, legally_incapable):
            if not cleaned_data["necessity_reason"]:
                error = forms.ValidationError(
                    _("Dit veld is verplicht."), code="required"
                )
                self.add_error("necessity_reason", error)


class StudyDesignForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["has_intervention", "has_observation", "has_sessions"]

    def clean(self):
        """
        Check for conditional requirements:
        - at least one of the fields has to be checked
        """
        cleaned_data = super(StudyDesignForm, self).clean()
        if not (
            cleaned_data.get("has_intervention")
            or cleaned_data.get("has_observation")
            or cleaned_data.get("has_sessions")
        ):
            msg = _("Je dient minstens één van de opties te selecteren")
            self.add_error("has_sessions", forms.ValidationError(msg, code="required"))


class StudyConsentForm(ConditionalModelForm):
    class Meta:
        model = Documents
        fields = [
            "proposal",
            "study",
            "informed_consent",
            "briefing",
            "director_consent_declaration",
            "director_consent_information",
            "parents_information",
        ]
        widgets = {"proposal": forms.HiddenInput, "study": forms.HiddenInput}

    def clean(self):
        cleaned_data = super(StudyConsentForm, self).clean()


class StudyEndForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Study
        fields = [
            "deception",
            "deception_details",
            "negativity",
            "negativity_details",
            "stressful",
            "stressful_details",
            "risk",
            "risk_details",
        ]
        widgets = {
            "deception": BootstrapRadioSelect(),
            "negativity": BootstrapRadioSelect(),
            "stressful": BootstrapRadioSelect(),
            "risk": BootstrapRadioSelect(),
        }

    _soft_validation_fields = [
        "deception",
        "deception_details",
        "negativity",
        "negativity_details",
        "stressful",
        "stressful_details",
        "risk",
        "risk_detail",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Remove empty label from deception/negativity/stressful/risk field and reset the choices
        - mark_safe the labels of negativity/stressful/risk
        """
        self.study = kwargs.pop("study", None)

        super(StudyEndForm, self).__init__(*args, **kwargs)

        self.fields["deception"].empty_label = None
        self.fields["deception"].choices = YesNoDoubt.choices
        self.fields["negativity"].empty_label = None
        self.fields["negativity"].choices = YesNoDoubt.choices
        self.fields["stressful"].empty_label = None
        self.fields["stressful"].choices = YesNoDoubt.choices
        self.fields["risk"].empty_label = None
        self.fields["risk"].choices = YesNoDoubt.choices

        self.fields["negativity"].label = mark_safe(self.fields["negativity"].label)
        self.fields["stressful"].label = mark_safe(self.fields["stressful"].label)
        self.fields["risk"].label = mark_safe(self.fields["risk"].label)

        if not self.study.has_sessions:
            del self.fields["deception"]
            del self.fields["deception_details"]

    def clean(self):
        """
        Check for conditional requirements:
        - If deception is set to yes, make sure deception_details has been filled out
        - If negativity is set to yes, make sure negativity_details has been filled out
        - If stressful is set to yes, make sure stressful_details has been filled out
        - If risk is set to yes, make sure risk_details has been filled out
        """
        cleaned_data = super(StudyEndForm, self).clean()

        # TODO: find a way to hide this on the first view
        self.mark_soft_required(cleaned_data, "negativity", "stressful", "risk")

        if "deception" in self.fields:
            self.mark_soft_required(cleaned_data, "deception")

        self.check_dependency_list(
            cleaned_data,
            "deception",
            "deception_details",
            f1_value_list=[YesNoDoubt.YES, YesNoDoubt.DOUBT],
        )
        self.check_dependency_list(
            cleaned_data,
            "negativity",
            "negativity_details",
            f1_value_list=[YesNoDoubt.YES, YesNoDoubt.DOUBT],
        )
        self.check_dependency_list(
            cleaned_data,
            "stressful",
            "stressful_details",
            f1_value_list=[YesNoDoubt.YES, YesNoDoubt.DOUBT],
        )
        self.check_dependency_list(
            cleaned_data,
            "risk",
            "risk_details",
            f1_value_list=[YesNoDoubt.YES, YesNoDoubt.DOUBT],
        )


class StudyUpdateAttachmentsForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = [
            # 'passive_consent',
            "informed_consent",
            "briefing",
            "director_consent_declaration",
            "director_consent_information",
            "parents_information",
        ]
        widgets = {
            # 'passive_consent': forms.HiddenInput
        }


class SessionStartForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["sessions_number"]

    def __init__(self, *args, **kwargs):
        """
        - Set the sessions_number field as required
        """
        super(SessionStartForm, self).__init__(*args, **kwargs)
        self.fields["sessions_number"].required = True
