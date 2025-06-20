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
    BootstrapCheckboxInput,
    BootstrapSelect,
    SearchableSelectWidget,
    DateInput,
    SplitDateTimeWidget,
    BootstrapSplitDateTimeWidget,
    TemplatedForm,
    TemplatedModelForm,
    TemplatedFormTextField,
)


class StudyForm(SoftValidationMixin, ConditionalModelForm):

    age_groups_header = TemplatedFormTextField(
        header=_("De leeftijdsgroep van je deelnemers"), header_element="h4"
    )

    legally_incapable_header = TemplatedFormTextField(
        header=_("Wilsonbekwaamheid"), header_element="h4"
    )

    necessity_header = TemplatedFormTextField(
        header=_("Noodzakelijkheid"), header_element="h4"
    )

    recruitment_header = TemplatedFormTextField(
        header=_("Werving"), header_element="h4"
    )

    compensation_header = TemplatedFormTextField(
        header=_("Compensatie"), header_element="h4"
    )

    hierarchy_header = TemplatedFormTextField(
        header=_("Hiërarchie"), header_element="h4"
    )

    class Meta:
        model = Study
        fields = [
            "age_groups_header",
            "age_groups",
            "legally_incapable_header",
            "legally_incapable",
            "legally_incapable_details",
            "necessity_header",
            "necessity",
            "necessity_reason",
            "recruitment_header",
            "recruitment",
            "recruitment_details",
            "compensation_header",
            "compensation",
            "compensation_details",
            "hierarchy_header",
            "hierarchy",
            "hierarchy_details",
        ]
        widgets = {
            "age_groups": BootstrapCheckboxSelectMultiple(),
            "legally_incapable": BootstrapRadioSelect(choices=YES_NO),
            "hierarchy": BootstrapRadioSelect(choices=YES_NO),
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
        self.fields["legally_incapable"].css_classes = " uu-form-no-gap"

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

        self.mark_soft_required(cleaned_data, "compensation", "hierarchy")

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


class PersonalDataForm(SoftValidationMixin, ConditionalModelForm):

    class Meta:
        model = Study
        fields = [
            "legal_basis",
            "has_special_details",
            "special_details",
            "traits",
            "traits_details",
        ]
        widgets = {
            "has_special_details": BootstrapRadioSelect(choices=YES_NO),
            "special_details": BootstrapCheckboxSelectMultiple(),
            "traits": BootstrapCheckboxSelectMultiple(),
            "legal_basis": BootstrapRadioSelect(),
        }

    _soft_validation_fields = [
        "legal_basis",
        "has_special_details",
        "special_details",
        "traits",
        "traits_details",
    ]

    def __init__(self, *args, **kwargs):

        super(PersonalDataForm, self).__init__(*args, **kwargs)

        self.fields["legal_basis"].empty_label = None
        self.fields["legal_basis"].choices = Study.LegalBases.choices

    def clean(self):
        """
        Check for conditional requirements:
        - If a trait which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(PersonalDataForm, self).clean()

        if cleaned_data["has_special_details"] is None:
            self.add_error("has_special_details", _("Dit veld is verplicht."))

        if cleaned_data["legal_basis"] is None:
            self.add_error("legal_basis", _("Selecteer een van de opties."))

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


class RegistrationForm(
    SoftValidationMixin,
    ConditionalModelForm,
):

    class Meta:
        model = Study
        fields = [
            "registrations",
            "registrations_details",
            "registration_kinds",
            "registration_kinds_details",
        ]
        widgets = {
            "registrations": BootstrapCheckboxSelectMultiple(),
            "registration_kinds": BootstrapCheckboxSelectMultiple(),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If a registration which needs a kind has been checked, make sure the kind is selected
        - If a registration which needs details has been checked, make sure the details are filled
        - If a registration_kind which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(RegistrationForm, self).clean()

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


class StudyDesignForm(
    SoftValidationMixin,
    TemplatedModelForm,
):

    # This form uses a custom template for rendering the form part.
    # As it needs are a bit specific
    template_name = "studies/study_design_form.html"

    class Meta:
        model = Study
        fields = [
            "has_intervention",
            "has_observation",
            "has_sessions",
        ]
        widgets = {
            "has_intervention": BootstrapCheckboxInput(),
            "has_observation": BootstrapCheckboxInput(),
            "has_sessions": BootstrapCheckboxInput(),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - at least one of the fields has to be checked
        """
        cleaned_data = super(StudyDesignForm, self).clean()

        if not True in cleaned_data.values():
            self.add_error(None, _("Er is nog geen onderzoekstype geselecteerd."))


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
            "risk",
            "risk_details",
        ]
        widgets = {
            "deception": BootstrapRadioSelect(),
            "negativity": BootstrapRadioSelect(),
            "risk": BootstrapRadioSelect(),
        }

    _soft_validation_fields = [
        "deception",
        "deception_details",
        "negativity",
        "negativity_details",
        "risk",
        "risk_detail",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Remove empty label from deception/negativity/risk field and reset the choices
        - mark_safe the labels of negativity/risk
        """

        self.choice_fields = (
            "deception",
            "negativity",
            "risk",
        )

        super(StudyEndForm, self).__init__(*args, **kwargs)

        for field in self.choice_fields:
            self.fields[field].choices = YesNoDoubt.choices

        self.fields["negativity"].label = mark_safe(self.fields["negativity"].label)
        self.fields["risk"].label = mark_safe(self.fields["risk"].label)

        if not self.instance.has_sessions:
            del self.fields["deception"]
            del self.fields["deception_details"]

        # If we have an existing instance and we're not POSTing,
        # run a initial clean
        if self.instance.pk and "data" not in kwargs:
            self.initial_clean()

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
        self.mark_soft_required(cleaned_data, "negativity", "risk")

        if "deception" in self.fields:
            self.mark_soft_required(cleaned_data, "deception")

        for field in self.choice_fields:
            self.check_dependency_list(
                cleaned_data,
                f"{field}",
                f"{field}_details",
                f1_value_list=[YesNoDoubt.YES, YesNoDoubt.DOUBT],
            )


class StudyUpdateAttachmentsForm(TemplatedModelForm):
    class Meta:
        model = Documents
        fields = [
            "informed_consent",
            "briefing",
            "director_consent_declaration",
            "director_consent_information",
            "parents_information",
        ]
