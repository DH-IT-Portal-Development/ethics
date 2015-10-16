from django import forms
from django.utils.translation import ugettext as _

from .models import Decision

yes_no = [(True, _('akkoord')), (False, _('niet akkoord'))]


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
