# -*- encoding: utf-8 -*-

from braces.forms import UserKwargModelFormMixin
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from django.utils.translation import gettext_lazy as _
from django.utils.functional import lazy
from django.utils.safestring import mark_safe, SafeString
from django.utils import timezone

mark_safe_lazy = lazy(mark_safe, SafeString)

from main.forms import ConditionalModelForm, SoftValidationMixin
from main.models import YesNoDoubt
from main.utils import YES_NO, get_users_as_list
from .field import ParentChoiceModelField
from .models import Proposal, Relation, Wmo
from .utils import check_local_facilities
from .validators import UniqueTitleValidator

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


class ProposalForm(UserKwargModelFormMixin, SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Proposal
        fields = [
            "title",
            "date_start",
            "institution",
        ]
        widgets = {
            "date_start": DateInput(),
            "institution": BootstrapRadioSelect(),
        }
        error_messages = {
            "title": {
                "unique": _("Er bestaat al een aanvraag met deze titel."),
            },
        }

    def __init__(self, *args, **kwargs):
        """
        - Make sure all non-revision/non-amendment studies have an unique name
        """

        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields["institution"].empty_label = None

        # Only revisions or amendments are allowed to have a title that's not
        # unique.
        if not self.instance or not self.instance.is_revision:
            self.fields["title"].validators.append(UniqueTitleValidator(self.instance))

    def clean(self):
        cleaned_data = super(ProposalForm, self).clean()

        self.mark_soft_required(cleaned_data, "date_start")


class ResearcherForm(
    UserKwargModelFormMixin, SoftValidationMixin, ConditionalModelForm
):
    class Meta:
        model = Proposal
        fields = [
            "relation",
            "student_program",
            "student_context",
            "student_context_details",
            "student_justification",
            "supervisor",
        ]
        widgets = {
            "relation": BootstrapRadioSelect(),
            "student_context": BootstrapRadioSelect(),
            "supervisor": SearchableSelectWidget(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Remove empty label from relation field
        - Don't allow to pick yourself or a superuser as supervisor, unless you already are
        - Add a None-option for supervisor
        - If this is a practice Proposal, limit the relation choices
        """

        super(ResearcherForm, self).__init__(*args, **kwargs)
        self.fields["relation"].empty_label = None
        self.fields["student_context"].empty_label = None

        supervisors = get_user_model().objects.exclude(pk=self.user.pk)

        instance = kwargs.get("instance")

        # If you are already defined as a supervisor, we have to set it to you
        if instance is not None and instance.supervisor == self.user:
            supervisors = [self.user]

        self.fields["supervisor"].choices = [
            (None, _("Selecteer..."))
        ] + get_users_as_list(supervisors)

        if instance.in_course:
            self.fields["relation"].queryset = Relation.objects.filter(
                check_in_course=True
            )
            self.fields["supervisor"].label = _("Docent")
            self.fields["supervisor"].help_text = _(
                "Vul hier de docent van \
de cursus in waarbinnen je deze portal moet doorlopen. De docent kan na afloop \
de aanvraag inkijken in de portal. De studie zal niet in het semipublieke archief \
van het FETC-GW worden opgenomen."
            )

        if instance.is_pre_assessment:
            self.fields["relation"].queryset = Relation.objects.filter(
                check_pre_assessment=True
            )

    def clean(self):
        """
        Check for conditional requirements:
        - If relation needs supervisor, make sure supervisor is set
        - If relation needs supervisor, make sure supervisor is a different person
        """
        cleaned_data = super(ResearcherForm, self).clean()

        relation = cleaned_data.get("relation")
        supervisor = cleaned_data.get("supervisor")

        if relation:
            if relation.needs_supervisor and not supervisor:
                error = forms.ValidationError(
                    _("Je dient een promotor/begeleider op te geven."), code="required"
                )
                self.add_error("supervisor", error)

            if (
                relation.needs_supervisor
                and supervisor == self.user
                and self.instance.status != Proposal.Statuses.SUBMITTED_TO_SUPERVISOR
            ):
                error = forms.ValidationError(
                    _("Je kunt niet jezelf als promotor/begeleider opgeven.")
                )
                self.add_error("supervisor", error)

            if relation.check_in_course:
                self.mark_soft_required(cleaned_data, "student_context")
                self.mark_soft_required(cleaned_data, "student_justification")

        self.check_dependency_singular(
            cleaned_data, "relation", "check_in_course", "student_program"
        )
        self.check_dependency_singular(
            cleaned_data, "student_context", "needs_details", "student_context_details"
        )
        self.check_dependency_singular(
            cleaned_data, "relation", "check_in_course", "student_justification"
        )


class OtherResearchersForm(
    UserKwargModelFormMixin, SoftValidationMixin, ConditionalModelForm
):
    class Meta:
        model = Proposal
        fields = [
            "other_applicants",
            "applicants",
            "other_stakeholders",
            "stakeholders",
        ]
        labels = {
            "other_stakeholders": mark_safe_lazy(
                _(
                    "Zijn er nog andere onderzoekers bij deze aanvraag betrokken "
                    "die <strong>niet</strong> geaffilieerd zijn aan een van de "
                    "onderzoeksinstituten van de Faculteit Geestwetenschappen van de "
                    "UU? "
                )
            ),
        }
        widgets = {
            "other_applicants": BootstrapRadioSelect(choices=YES_NO),
            "other_stakeholders": BootstrapRadioSelect(choices=YES_NO),
            "applicants": SearchableSelectWidget(),
        }

    _soft_validation_fields = [
        "other_applicants",
        "other_stakeholders",
        "stakeholders",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Don't allow to pick a superuser as applicant
        """
        super(OtherResearchersForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.get("instance")

        # Needed to set the widget into multiple mode
        # TODO: write a DSC widget that has this enabled by default
        self.fields["applicants"].widget.allow_multiple_selected = True

        applicants = get_user_model().objects.all()

        self.fields["other_stakeholders"].label = mark_safe(
            self.fields["other_stakeholders"].label
        )

        self.fields["applicants"].choices = get_users_as_list(applicants)

    def clean(self):
        """
        Check for conditional requirements:
        - If other_applicants is checked, make sure applicants are set
        - If other_stakeholders is checked, make sure stakeholders is not empty
        - Make sure the user is listed in applicants
        """
        cleaned_data = super(OtherResearchersForm, self).clean()

        other_applicants = cleaned_data.get("other_applicants")
        applicants = cleaned_data.get("applicants")

        # Always make sure the applicant is actually in the applicants list
        if self.user not in applicants and self.user != self.instance.supervisor:
            error = forms.ValidationError(
                _("Je hebt jezelf niet als onderzoekers geselecteerd."), code="required"
            )
            self.add_error("applicants", error)
        elif other_applicants and len(applicants) == 1:
            error = forms.ValidationError(
                _("Je hebt geen andere onderzoekers geselecteerd."), code="required"
            )
            self.add_error("applicants", error)

        self.check_dependency(cleaned_data, "other_stakeholders", "stakeholders")


class FundingForm(UserKwargModelFormMixin, SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Proposal
        fields = [
            "funding",
            "funding_details",
            "funding_name",
        ]
        widgets = {
            "funding": BootstrapCheckboxSelectMultiple(),
        }
        error_messages = {
            "title": {
                "unique": _("Er bestaat al een aanvraag met deze titel."),
            },
        }

    _soft_validation_fields = [
        "funding",
        "funding_details",
        "funding_name",
    ]

    def clean(self):
        cleaned_data = super(FundingForm, self).clean()

        self.check_dependency_multiple(
            cleaned_data, "funding", "needs_details", "funding_details"
        )
        self.check_dependency_multiple(
            cleaned_data, "funding", "needs_name", "funding_name"
        )


class ResearchGoalForm(
    UserKwargModelFormMixin, SoftValidationMixin, ConditionalModelForm
):
    class Meta:
        model = Proposal
        fields = [
            "summary",
            "pre_assessment_pdf",
            "self_assessment",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"cols": 50}),
        }

    _soft_validation_fields = [
        "summary",
        "pre_assessment_pdf",
        "self_assessment",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Remove summary for preliminary assessment Proposals
        - Set pre_assessment_pdf required for preliminary assessment Proposals, otherwise remove
        """

        super(ResearchGoalForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.get("instance")

        if self.instance.is_pre_assessment:
            self.fields["pre_assessment_pdf"].required = True
            del self.fields["summary"]
        else:
            del self.fields["pre_assessment_pdf"]

    def clean(self):
        cleaned_data = super(ResearchGoalForm, self).clean()

        if not self.instance.is_pre_assessment:
            self.mark_soft_required(cleaned_data, "summary")

        # Add an error if self_assessment is missing
        self_assessment = cleaned_data.get("self_assessment")
        if self_assessment == "":
            self.add_error(
                "self_assessment",
                forms.ValidationError(
                    _(
                        "Dit veld is verplicht, maar je kunt later terugkomen om hem \
                    verder in te vullen."
                    ),
                    code="required",
                ),
            )


class PreApprovedForm(
    UserKwargModelFormMixin, SoftValidationMixin, ConditionalModelForm
):
    class Meta:
        model = Proposal
        fields = [
            "is_pre_approved",
            "pre_approval_institute",
            "pre_approval_pdf",
        ]
        widgets = {
            "is_pre_approved": BootstrapRadioSelect(choices=YES_NO),
        }

    _soft_validation_fields = [
        "pre_approval_institute",
        "pre_approval_pdf",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Set pre_assessment_pdf required for preliminary assessment Proposals, otherwise remove
        """

        super(PreApprovedForm, self).__init__(*args, **kwargs)

        instance = kwargs.get("instance")

        if instance.is_pre_approved:
            self.fields["pre_approval_institute"].required = True
            self.fields["pre_approval_pdf"].required = True
        else:
            del self.fields["is_pre_approved"]
            del self.fields["pre_approval_institute"]
            del self.fields["pre_approval_pdf"]

    def clean(self):
        """
        - If this is a pre approved proposal, make sure people say yes to that question
        - If this is a pre approved proposal, make sure people fill in the correct fields
        """
        cleaned_data = super(PreApprovedForm, self).clean()

        if "is_pre_approved" in cleaned_data:
            if not cleaned_data["is_pre_approved"]:
                error = forms.ValidationError(
                    _(
                        "Indien je geen toestemming hebt van een andere ethische commissie, dien je het normale formulier in "
                        'te vullen. Ga terug naar de startpagina, en selecteer "Een nieuwe aanvraag aanmelden (from scratch in '
                        'een leeg formulier)" of "Een nieuwe aanvraag aanmelden (vanuit een kopie van een oude aanvraag)".'
                    )
                )
                self.add_error("is_pre_approved", error)

            self.check_dependency(cleaned_data, "is_pre_approved", "pre_approval_pdf")
            self.check_dependency(
                cleaned_data, "is_pre_approved", "pre_approval_institute"
            )


class ProposalStartPracticeForm(TemplatedForm):
    practice_reason = forms.ChoiceField(
        label=_("Ik maak een oefenaanvraag aan"),
        choices=Proposal.PracticeReasons.choices,
        widget=BootstrapRadioSelect(),
    )


class BaseProposalCopyForm(UserKwargModelFormMixin, TemplatedModelForm):
    class Meta:
        model = Proposal
        fields = ["parent", "is_revision"]
        widgets = {
            "is_revision": forms.HiddenInput(),
        }

    # TODO: figure out if we need to change widgets here
    parent = ParentChoiceModelField(
        queryset=Proposal.objects.all(),
        label=_("Te kopiëren aanvraag"),
        help_text=_(
            "Dit veld toont enkel aanvragen waar je zelf een medeuitvoerende " "bent."
        ),
    )

    def __init__(self, *args, **kwargs):
        super(BaseProposalCopyForm, self).__init__(*args, **kwargs)

        self.fields["parent"].queryset = self._get_parent_queryset()

    def _get_parent_queryset(self):
        # Return all non-pre-assessments, that are not currently in review
        return (
            Proposal.objects.filter(is_pre_assessment=False)
            .filter(
                Q(
                    applicants=self.user,
                )
                | Q(supervisor=self.user)
            )
            .filter(
                Q(status=Proposal.Statuses.DRAFT)
                | Q(status__gte=Proposal.Statuses.DECISION_MADE)
            )
            .distinct()
        )


class ProposalCopyForm(BaseProposalCopyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only revisions or amendments are allowed to have a title that's not
        # unique, so we have to attach a validator to this version of the form

        # The uniqueness validator has been temporarily disabled to allow for
        # the removal of the title field in its entirety.
        # self.fields['title'].validators.append(UniqueTitleValidator())


class RevisionProposalCopyForm(BaseProposalCopyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["parent"].label = _("Te reviseren aanvraag")
        self.fields["parent"].help_text = _(
            "Dit veld toont enkel ingediende,"
            " (nog) niet goedgekeurde aanvragen "
            "waar jij een "
            "medeuitvoerende bent."
        )

    def _get_parent_queryset(self):
        # Select non-pre-assessments that have been reviewed and rejected and
        # haven't been parented yet.
        # Those are eligible for revisions
        return (
            Proposal.objects.filter(
                is_pre_assessment=False,
                status=Proposal.Statuses.DECISION_MADE,
                status_review=False,
                children__isnull=True,
            )
            .filter(
                Q(
                    applicants=self.user,
                )
                | Q(supervisor=self.user)
            )
            .distinct()
        )


class AmendmentProposalCopyForm(BaseProposalCopyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["parent"].label = _("Te amenderen aanvraag")
        self.fields["parent"].help_text = _(
            "Dit veld toont enkel goedgekeurde"
            " aanvragen waar je zelf een "
            "medeuitvoerende bent."
        )

    def _get_parent_queryset(self):
        # Select non-pre-assessments that have been reviewed and approved and
        # haven't been parented yet.
        # Those are eligible for amendments
        return (
            Proposal.objects.filter(
                is_pre_assessment=False,
                status_review=True,
                children__isnull=True,
            )
            .filter(
                Q(
                    applicants=self.user,
                )
                | Q(supervisor=self.user)
            )
            .distinct()
        )


class ProposalConfirmationForm(TemplatedModelForm):
    class Meta:
        model = Proposal
        fields = ["date_confirmed", "confirmation_comments"]
        widgets = {"date_confirmed": DateInput}


class WmoForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Wmo
        fields = ["metc", "metc_details", "metc_institution", "is_medical"]
        widgets = {"metc": BootstrapRadioSelect(), "is_medical": BootstrapRadioSelect()}

    _soft_validation_fields = ["metc_details", "metc_institution", "is_medical"]

    def __init__(self, *args, **kwargs):
        """
        - Remove empty label from is_medical/is_behavioristic field and reset the choices
        """
        super(WmoForm, self).__init__(*args, **kwargs)
        self.fields["metc"].empty_label = None
        self.fields["metc"].choices = YesNoDoubt.choices
        self.fields["is_medical"].empty_label = None
        self.fields["is_medical"].choices = YesNoDoubt.choices

    def clean(self):
        """
        Check for conditional requirements:
        - If metc is checked, make sure institution is set and details are filled out
        - If metc is not checked, check if is_medical or is_behavioristic is set
        """
        cleaned_data = super(WmoForm, self).clean()

        if "metc" not in cleaned_data or not cleaned_data["metc"]:
            self.add_error("metc", _("Dit veld is verplicht om verder te " "gaan."))

        self.check_dependency(
            cleaned_data, "metc", "metc_details", f1_value=YesNoDoubt.YES
        )
        self.check_dependency(
            cleaned_data,
            "metc",
            "metc_institution",
            f1_value=YesNoDoubt.YES,
            error_message=_("Je dient een instelling op te geven."),
        )
        self.check_dependency_list(
            cleaned_data,
            "metc",
            "is_medical",
            f1_value_list=[YesNoDoubt.NO, YesNoDoubt.DOUBT],
        )


class WmoApplicationForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Wmo
        fields = [
            "metc_application",
            "metc_decision",
            "metc_decision_pdf",
        ]
        widgets = {
            "metc_application": BootstrapRadioSelect(choices=YES_NO),
            "metc_decision": BootstrapRadioSelect(choices=YES_NO),
        }

    _soft_validation_fields = [
        "metc_application",
        "metc_decision",
        "metc_decision_pdf",
    ]

    def clean(self):
        """
        Check for conditional requirements:
        - An metc_decision is always required
        """
        cleaned_data = super(WmoApplicationForm, self).clean()

        # A PDF is always required for this form, but it's in ProposalSubmit
        # validation that this is actually rejected. Otherwise this is soft
        # validation
        if cleaned_data["metc_decision_pdf"] == None:
            from django.forms import ValidationError

            self.add_error(
                "metc_decision_pdf",
                ValidationError(
                    _("In dit geval is een beslissing van een METC vereist"),
                ),
            )

        return cleaned_data  # Sticking to Django conventions


class StudyStartForm(SoftValidationMixin, ConditionalModelForm):
    study_name_1 = forms.CharField(
        label=_("Naam traject 1"),
        max_length=15,
        required=False,
        help_text=_(
            "Geef elk traject hieronder een behulpzame naam van maximaal 15 karakters."
        ),
    )
    study_name_2 = forms.CharField(
        label=_("Naam traject 2"), max_length=15, required=False
    )
    study_name_3 = forms.CharField(
        label=_("Naam traject 3"), max_length=15, required=False
    )
    study_name_4 = forms.CharField(
        label=_("Naam traject 4"), max_length=15, required=False
    )
    study_name_5 = forms.CharField(
        label=_("Naam traject 5"), max_length=15, required=False
    )
    study_name_6 = forms.CharField(
        label=_("Naam traject 6"), max_length=15, required=False
    )
    study_name_7 = forms.CharField(
        label=_("Naam traject 7"), max_length=15, required=False
    )
    study_name_8 = forms.CharField(
        label=_("Naam traject 8"), max_length=15, required=False
    )
    study_name_9 = forms.CharField(
        label=_("Naam traject 9"), max_length=15, required=False
    )
    study_name_10 = forms.CharField(
        label=_("Naam traject 10"), max_length=15, required=False
    )

    class Meta:
        model = Proposal
        fields = [
            "studies_similar",
            "studies_number",
            "study_name_1",
            "study_name_2",
            "study_name_3",
            "study_name_4",
            "study_name_5",
            "study_name_6",
            "study_name_7",
            "study_name_8",
            "study_name_9",
            "study_name_10",
        ]
        widgets = {
            "studies_similar": BootstrapRadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Proposal for later reference
        - Set initial data for the study_name fields
        """
        self.proposal = kwargs.pop("proposal", None)

        super(StudyStartForm, self).__init__(*args, **kwargs)

        for field, name in self._get_study_names().items():
            self.fields[field].initial = name

    def _get_study_names(
        self,
    ):
        names = {}
        for n, study in enumerate(self.proposal.study_set.all()):
            study_name = "study_name_" + str(n + 1)
            names[study_name] = study.name
        return names

    def clean(self):
        """
        Check for conditional requirements:
        - If studies_similar is not set, add a required error
        - If studies_similar is set to False, make sure studies_number is set (and higher than 2)
        - If studies_number is set, make sure the corresponding name fields are filled.
        """
        # Start with study names
        cleaned_data = self._get_study_names()
        # Update with provided form data
        cleaned_data.update(super().clean())

        if cleaned_data["studies_similar"] is None:
            self.add_error(
                "studies_similar", _("Dit veld is verplicht om " "verder te gaan.")
            )
        elif not cleaned_data["studies_similar"]:
            nr_studies = cleaned_data["studies_number"]
            if cleaned_data["studies_number"] < 2:
                self.add_error(
                    "studies_number",
                    _(
                        "Als niet dezelfde trajecten worden doorlopen, moeten er minstens twee verschillende trajecten zijn."
                    ),
                )
            for n in range(nr_studies):
                if n >= 10:
                    break
                study_name = "study_name_" + str(n + 1)
                if not cleaned_data[study_name]:
                    self.add_error(study_name, _("Dit veld is verplicht."))


class ProposalDataManagementForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Proposal
        fields = ["privacy_officer", "dmp_file"]
        widgets = {
            "privacy_officer": BootstrapRadioSelect(choices=YES_NO),
        }

    def clean(self):
        cleaned_data = super(ProposalDataManagementForm, self).clean()

        if cleaned_data["privacy_officer"] is None:
            self.add_error(
                "privacy_officer", _("Dit veld is verplicht om verder te gaan.")
            )


class ProposalUpdateDataManagementForm(TemplatedModelForm):
    class Meta:
        model = Proposal
        fields = ["dmp_file"]


class ProposalUpdateDateStartForm(TemplatedModelForm):
    date_start = DateField(label=_("Nieuwe beoogde startdatum"))

    class Meta:
        model = Proposal
        fields = ["date_start"]


class ProposalSubmitForm(ConditionalModelForm):
    class Meta:
        model = Proposal
        fields = ["comments", "inform_local_staff", "embargo", "embargo_end_date"]
        widgets = {
            "inform_local_staff": BootstrapRadioSelect(choices=YES_NO),
            "embargo": BootstrapRadioSelect(choices=YES_NO),
            "embargo_end_date": DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Mark the label of inform_local_staff as safe
        - Check if the inform_local_staff question should be asked
        """
        self.proposal = kwargs.pop("proposal", None)

        # Needed for POST data
        self.request = kwargs.pop("request", None)

        super(ProposalSubmitForm, self).__init__(*args, **kwargs)

        self.fields["inform_local_staff"].label_suffix = ""

        self.fields["inform_local_staff"].label = mark_safe(
            self.fields["inform_local_staff"].label
        )

        if not check_local_facilities(self.proposal):
            del self.fields["inform_local_staff"]

    def clean(self):
        """
        Check if the Proposal is complete:
        - Do all Studies have informed consent/briefing?
        - If the inform_local_staff question is asked, it is required
        - Was the embargo question answered and, if so, is the end date within two years from now?
        """
        from studies.models import Documents

        cleaned_data = super(ProposalSubmitForm, self).clean()

        if (
            not self.instance.is_pre_assessment
            and not self.instance.is_practice()
            and not "js-redirect-submit" in self.request.POST
            and not "save_back" in self.request.POST
        ):
            if (
                check_local_facilities(self.proposal)
                and cleaned_data["inform_local_staff"] is None
            ):
                self.add_error("inform_local_staff", _("Dit veld is verplicht."))

            for study in self.instance.study_set.all():
                documents = Documents.objects.get(study=study)

                if not documents.informed_consent:
                    self.add_error(
                        "comments",
                        _(
                            "Toestemmingsverklaring voor traject {} nog niet toegevoegd."
                        ).format(study.order),
                    )
                if not documents.briefing:
                    self.add_error(
                        "comments",
                        _(
                            "Informatiebrief voor traject {} nog niet toegevoegd."
                        ).format(study.order),
                    )

            if cleaned_data["embargo"] is None:
                self.add_error("embargo", _("Dit veld is verplicht."))

            embargo_end_date = cleaned_data["embargo_end_date"]
            two_years_from_now = timezone.now().date() + timezone.timedelta(days=730)

            if embargo_end_date is not None and embargo_end_date > two_years_from_now:
                self.add_error(
                    "embargo_end_date",
                    _(
                        "De embargo-periode kan maximaal 2 jaar zijn. Kies een datum binnen 2 jaar van vandaag."
                    ),
                )


class KnowledgeSecurityForm(SoftValidationMixin, ConditionalModelForm):

    class Meta:
        model = Proposal
        fields = [
            "knowledge_security",
            "knowledge_security_details",
            "researcher_risk",
            "researcher_risk_details",
        ]
        widgets = {
            "knowledge_security": BootstrapRadioSelect(),
            "researcher_risk": BootstrapRadioSelect(),
        }

    _soft_validation_fields = [
        "knowledge_security",
        "knowledge_security_details",
        "researcher_risk",
        "researcher_risk_details",
    ]

    def __init__(self, *args, **kwargs):
        """
        - Set the Study for later reference
        - Remove empty label from fields and reset the choices
        """
        super(KnowledgeSecurityForm, self).__init__(*args, **kwargs)

        self.base_fields = (
            "knowledge_security",
            "researcher_risk",
        )
        for field in self.base_fields:
            self.fields[field].empty_label = None
            self.fields[field].choices = YesNoDoubt.choices
        
    def clean(self):
        """
        Check for conditional requirements:
        - If deception is set to yes, make sure deception_details has been filled out
        - If negativity is set to yes, make sure negativity_details has been filled out
        - If risk is set to yes, make sure risk_details has been filled out
        """
        cleaned_data = super(KnowledgeSecurityForm, self).clean()

        self.mark_soft_required(
            cleaned_data, "knowledge_security", "researcher_risk"
        )

        for field in self.base_fields:
            self.check_dependency_list(
                cleaned_data,
                f"{field}",
                f"{field}_details",
                f1_value_list=[YesNoDoubt.YES, YesNoDoubt.DOUBT],
            )


class TranslatedConsentForm(SoftValidationMixin, ConditionalModelForm):
    class Meta:
        model = Proposal
        fields = ["translated_forms", "translated_forms_languages"]
        widgets = {
            "translated_forms": BootstrapRadioSelect(choices=YES_NO),
        }

    _soft_validation_fields = ["translated_forms", "translated_forms_languages"]

    def clean(self):
        cleaned_data = super(TranslatedConsentForm, self).clean()

        if cleaned_data["translated_forms"] is None:
            self.add_error(
                "translated_forms", _("Dit veld is verplicht om verder te gaan.")
            )

        elif (
            cleaned_data["translated_forms"] == True
            and not cleaned_data["translated_forms_languages"]
        ):
            self.add_error(
                "translated_forms_languages",
                _("Vul in in welke talen de formulieren worden vertaald."),
            )
