from django.forms import forms
from django.utils.translation import gettext as _

from .models import Proposal


def validate_title_unique(value):
    if Proposal.objects.filter(title=value).exists():
        raise forms.ValidationError(_('Er bestaat al een studie met deze '
                                      'titel.'), code='unique')
