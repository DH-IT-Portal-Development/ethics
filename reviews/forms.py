from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from main.forms import ConditionalModelForm
from main.utils import YES_NO, get_reviewers_from_groups, is_secretary
from proposals.models import Proposal
from .models import Review, Decision

from django.core.exceptions import ValidationError

SHORT_LONG_REVISE = [(True, _('korte (2-weken) route')),
                     (False, _('lange (4-weken) route')),
                     (None, _('direct naar revisie'))]


class ChangeChamberForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['reviewing_committee']

    def __init__(self, *args, **kwargs):
        super(ChangeChamberForm, self).__init__(*args, **kwargs)

        general_chamber = Group.objects.get(name=settings.GROUP_GENERAL_CHAMBER)
        linguistics_chamber = Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER)

        self.fields['reviewing_committee'].choices = (
            (general_chamber.pk, _('Algemene Kamer')),
            (linguistics_chamber.pk, _('Linguïstiek Kamer')),
        )


class ReviewAssignForm(ConditionalModelForm):
    class Meta:
        model = Review
        fields = ['short_route']
        widgets = {
            'short_route': forms.RadioSelect(choices=SHORT_LONG_REVISE),
        }

    def __init__(self, *args, **kwargs):
        """
        - Adds a field to select reviewers for this Proposal
        """
        super(ReviewAssignForm, self).__init__(*args, **kwargs)

        # reviewers = get_reviewers_from_group(
        #     self.instance.proposal.reviewing_committee
        # )
        reviewers = get_reviewers_from_groups(
            [
                settings.GROUP_GENERAL_CHAMBER,
                settings.GROUP_LINGUISTICS_CHAMBER,
                settings.GROUP_SECRETARY
            ]
        )

        self.fields['reviewers'] = forms.ModelMultipleChoiceField(
            initial=self.instance.current_reviewers(),
            queryset=reviewers,
            widget=forms.SelectMultiple(attrs={'data-placeholder': _('Selecteer de commissieleden')}),
            required=False
        )

    def clean_reviewers(self):
        reviewers = self.cleaned_data['reviewers']
        
        # To make sure at least one secretary is assigned,
        # comment out the following return statement
        return self.cleaned_data['reviewers']
    
        for user in reviewers:
            if is_secretary(user):
                break
        else:
            raise ValidationError(
                _('Er moet tenminste één secretaris geselecteerd worden.'),
                code='no_secretary')

        return self.cleaned_data['reviewers']


class ReviewCloseForm(forms.ModelForm):
    in_archive = forms.BooleanField(initial=True, required=False)
    has_minor_revision = forms.BooleanField(initial=False, required=False)
    minor_revision_description = forms.Field(required=False)

    class Meta:
        model = Review
        fields = [
            'continuation',
            'has_minor_revision',
            'minor_revision_description',
            'in_archive',
        ]
        widgets = {
            'continuation': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Remove long route option if this was already the long route.
        - Set the label for in_archive
        """
        allow_long_route_continuation = kwargs.pop('allow_long_route_continuation', False)
        super(ReviewCloseForm, self).__init__(*args, **kwargs)
        if not allow_long_route_continuation:
            self.fields['continuation'].choices = [x for x in Review.CONTINUATIONS if x[0] != Review.LONG_ROUTE]

        self.fields['in_archive'].label = _('Voeg deze studie toe aan het archief')
        self.fields['in_archive'].widget = forms.RadioSelect(choices=YES_NO)

        self.fields['has_minor_revision'].label = _('Is er een revisie geweest na het indienen van deze studie?')
        self.fields['has_minor_revision'].widget = forms.RadioSelect(choices=YES_NO)

        self.fields['minor_revision_description'].label = _('Opmerkingen over revisie')
        self.fields['minor_revision_description'].widget = forms.Textarea()


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ['go', 'comments']
        widgets = {
            'go': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """Removes the empty label for the go field, and sets it as required"""
        super(DecisionForm, self).__init__(*args, **kwargs)
        self.fields['go'].empty_label = None
        self.fields['go'].choices = Decision.APPROVAL
        self.fields['go'].required = True
