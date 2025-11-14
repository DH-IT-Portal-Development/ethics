from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from main.forms import ConditionalModelForm
from main.utils import YES_NO, get_reviewers_from_groups, is_secretary
from proposals.models import Proposal
from .models import Review, Decision

from cdh.core.forms import (
    DateField,
    BootstrapRadioSelect,
    SearchableSelectWidget,
    TemplatedModelForm,
    BootstrapCheckboxInput,
    TemplatedForm,
)

from django.core.exceptions import ValidationError


SHORT_LONG_REVISE = [
    (True, _("korte route of revisie (2-weken)")),
    (False, _("lange route (4-weken)")),
    (None, _("Direct terug naar aanvrager (Nog niet in behandeling)")),
]


class ChangeChamberForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["reviewing_committee"]

    def __init__(self, *args, **kwargs):
        super(ChangeChamberForm, self).__init__(*args, **kwargs)

        general_chamber = Group.objects.get(name=settings.GROUP_GENERAL_CHAMBER)
        linguistics_chamber = Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER)

        self.fields["reviewing_committee"].choices = (
            (general_chamber.pk, _("Algemene Kamer")),
            (linguistics_chamber.pk, _("Linguïstiek Kamer")),
        )


class ReviewAssignForm(ConditionalModelForm):
    class Meta:
        model = Review
        fields = ["short_route"]
        widgets = {
            "short_route": BootstrapRadioSelect(choices=SHORT_LONG_REVISE),
        }

    def __init__(self, *args, **kwargs):
        """
        - Adds a field to select reviewers for this Proposal
        """
        super(ReviewAssignForm, self).__init__(*args, **kwargs)

        reviewers = get_reviewers_from_groups(
            [
                settings.GROUP_GENERAL_CHAMBER,
                settings.GROUP_LINGUISTICS_CHAMBER,
                settings.GROUP_SECRETARY,
            ]
        )

        self.fields["reviewers"] = forms.ModelMultipleChoiceField(
            initial=self.instance.current_reviewers(),
            queryset=reviewers,
            widget=SearchableSelectWidget(),
            required=False,
        )

        self.fields["reviewers"].widget.allow_multiple_selected = True

    def clean_reviewers(self):
        reviewers = self.cleaned_data["reviewers"]

        if len(reviewers) == 0:
            raise ValidationError(
                _("Er moet tenminste één beoordelaar geselecteerd worden."),
                code="no_reviewer",
            )

        # See PR #188 if a secretary should be added to every review
        return self.cleaned_data["reviewers"]


class ReviewCloseForm(ConditionalModelForm):
    in_archive = forms.BooleanField(initial=True, required=False)
    has_minor_revision = forms.BooleanField(initial=False, required=False)
    minor_revision_description = forms.Field(required=False)

    class Meta:
        model = Review
        fields = [
            "continuation",
            "has_minor_revision",
            "minor_revision_description",
            "in_archive",
        ]
        widgets = {
            "continuation": BootstrapRadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Remove long route option if this was already the long route.
        - Set the label for in_archive
        """
        allow_long_route_continuation = kwargs.pop(
            "allow_long_route_continuation", False
        )
        super(ReviewCloseForm, self).__init__(*args, **kwargs)

        self.fields["continuation"].choices = Review.Continuations.choices
        # Reviews should only be discontinued at ReviewDiscontinueView
        discontinued_tuple: tuple = (
            Review.Continuations.DISCONTINUED.value,
            Review.Continuations.DISCONTINUED.label,
        )
        self.fields["continuation"].choices.remove(discontinued_tuple)

        if not allow_long_route_continuation:
            longroute_tuple: tuple = (
                Review.Continuations.LONG_ROUTE.value,
                Review.Continuations.LONG_ROUTE.label,
            )
            self.fields["continuation"].choices.remove(longroute_tuple)

        self.fields["in_archive"].label = _("Voeg deze aanvraag toe aan het archief")
        self.fields["in_archive"].widget = BootstrapRadioSelect(choices=YES_NO)

        self.fields["has_minor_revision"].label = _(
            "Is er een revisie geweest na het indienen van deze aanvraag?"
        )
        self.fields["has_minor_revision"].widget = BootstrapRadioSelect(choices=YES_NO)

        self.fields["minor_revision_description"].label = _("Opmerkingen over revisie")
        self.fields["minor_revision_description"].widget = forms.Textarea()


class ReviewDiscontinueForm(forms.ModelForm):
    confirm_discontinue = forms.BooleanField(
        initial=False, required=True, label=_("Bevestig beëindiging")
    )

    class Meta:
        model = Review
        fields = [
            "confirm_discontinue",
        ]

        widgets = {"confirm_discontinue": BootstrapCheckboxInput()}


class DecisionForm(TemplatedModelForm):
    class Meta:
        model = Decision
        fields = ["go", "comments"]
        widgets = {
            "go": BootstrapRadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """Removes the empty label for the go field, and sets it as required"""
        super(DecisionForm, self).__init__(*args, **kwargs)
        self.fields["go"].empty_label = None
        self.fields["go"].choices = Decision.Approval.choices
        self.fields["go"].required = True


class StartEndDateForm(TemplatedForm):
    start_date = DateField(label=_("Start datum periode:"))
    end_date = DateField(label=_("Eind datum periode:"))


class ReviewUpdateEmailCheckboxForm(TemplatedModelForm):
    class Meta:
        model = Review
        fields = ["email_checkbox"]
        widgets = {
            "email_checkbox": BootstrapRadioSelect(choices=YES_NO),
        }
