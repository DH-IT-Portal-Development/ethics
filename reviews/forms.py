from django import forms
from django.utils.translation import ugettext_lazy as _

from core.forms import ConditionalModelForm
from core.utils import YES_NO, get_reviewers
from .models import Review, Decision

SHORT_LONG_REVISE = [(True, _('korte (2-weken) route')), (False, _('lange (4-weken) route')), (None, _('direct naar revisie'))]


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
        self.fields['reviewers'] = forms.ModelMultipleChoiceField(
            initial=self.instance.current_reviewers(),
            queryset=get_reviewers(),
            widget=forms.SelectMultiple(attrs={'data-placeholder': _('Selecteer de commissieleden')}),
            required=False
        )


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
        allow_long_route_continuation = kwargs.pop('allow_long_route_continuation', False)
        super(ReviewCloseForm, self).__init__(*args, **kwargs)
        if not allow_long_route_continuation:
            self.fields['continuation'].choices = [x for x in Review.CONTINUATIONS if x[0] != Review.LONG_ROUTE]

        self.fields['in_archive'].label = _('Voeg deze studie toe aan het UiL OTS archief')
        self.fields['in_archive'].widget = forms.RadioSelect(choices=YES_NO)


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
