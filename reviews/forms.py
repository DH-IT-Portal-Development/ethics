from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from .models import Review, Decision

yes_no = [(True, _('akkoord')), (False, _('niet akkoord'))]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = []

    reviewers = forms.ModelMultipleChoiceField(queryset=get_user_model().objects.all())


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ['go', 'comments']
        widgets = {
            'go': forms.RadioSelect(choices=yes_no),
        }

    def __init__(self, *args, **kwargs):
        """Set the go field as required"""
        super(DecisionForm, self).__init__(*args, **kwargs)
        self.fields['go'].required = True
