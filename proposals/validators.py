from django.forms import forms
from django.utils.translation import gettext as _

from .models import Proposal


class UniqueTitleValidator:
    proposal = None

    def __init__(self, proposal: Proposal = None):
        self.proposal = proposal
        print(proposal)

    def __call__(self, value):
        qs = Proposal.objects.filter(title=value)

        if self.proposal:
            qs = qs.exclude(pk=self.proposal.pk)

        if qs.exists():
            raise forms.ValidationError(_('Er bestaat al een studie met deze '
                                          'titel.'), code='unique')