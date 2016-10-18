from django import forms
from django.utils.translation import ugettext_lazy as _

from core.utils import YES_NO, get_reviewers
from .models import Review, Decision

APPROVAL = [(True, _('goedgekeurd')), (False, _('niet goedgekeurd'))]
SHORT_LONG = [(True, _('korte (2-weken) route')), (False, _('lange (4-weken) route'))]


class ReviewAssignForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['short_route']
        widgets = {
            'short_route': forms.RadioSelect(choices=SHORT_LONG),
        }

    def __init__(self, *args, **kwargs):
        """
        - Adds a field to select reviewers for this Proposal
        """
        super(ReviewAssignForm, self).__init__(*args, **kwargs)
        current_reviewers = self.instance.current_reviewers()
        selectable_reviewers = get_reviewers()
        self.fields['reviewers'] = forms.ModelMultipleChoiceField(
            initial=current_reviewers,
            queryset=selectable_reviewers,
            widget=forms.SelectMultiple(attrs={'data-placeholder': _('Selecteer de commissieleden')}))


class ReviewCloseForm(forms.ModelForm):
    in_archive = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = Review
        fields = ['continuation', 'in_archive']
        widgets = {
            'continuation': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Remove long route option if this was already the long route.
        - Set the label for in_archive
        """
        short_route = kwargs.pop('short_route', False)
        super(ReviewCloseForm, self).__init__(*args, **kwargs)
        if not short_route:
            self.fields['continuation'].choices = [x for x in Review.CONTINUATIONS if x[0] != Review.LONG_ROUTE]

        self.fields['in_archive'].label = _('Voeg deze studie toe aan het UiL OTS archief')
        self.fields['in_archive'].widget = forms.RadioSelect(choices=YES_NO)


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ['go', 'comments']
        widgets = {
            'go': forms.RadioSelect(choices=APPROVAL),
        }

    def __init__(self, *args, **kwargs):
        """Sets the go field as required"""
        super(DecisionForm, self).__init__(*args, **kwargs)
        self.fields['go'].required = True
