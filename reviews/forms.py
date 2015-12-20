from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from .models import Review, Decision

COMMISSION = 'Commissie'
YES_NO = [(True, _('akkoord')), (False, _('niet akkoord'))]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = []

    def __init__(self, *args, **kwargs):
        """Adds a field to select reviewers for this Proposal"""
        super(ReviewForm, self).__init__(*args, **kwargs)
        reviewers = get_user_model().objects.filter(groups__name=COMMISSION)
        self.fields['reviewers'] = forms.ModelMultipleChoiceField(queryset=reviewers, 
            widget=forms.SelectMultiple(attrs={'data-placeholder': _('Selecteer de commissieleden')}))


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ['go', 'comments']
        widgets = {
            'go': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """Sets the go field as required"""
        super(DecisionForm, self).__init__(*args, **kwargs)
        self.fields['go'].required = True
