from django.forms import forms
from django.utils.translation import gettext as _



class UniqueTitleValidator:


    proposal = None

    def __init__(self, proposal = None):
        self.proposal = proposal

    def __call__(self, value):

        # Importing here to prevent circular import
        from .models import Proposal

        qs = Proposal.objects.filter(title=value)

        if self.proposal:
            qs = qs.exclude(pk=self.proposal.pk)

        if qs.exists():
            raise forms.ValidationError(_('Er bestaat al een studie met deze '
                                          'titel.'), code='unique')


def AVGUnderstoodValidator(value):

    if value != True:
        raise forms.ValidationError(
            _('Je dient kennis genomen te hebben van de AVG om jouw studie in '
              'te dienen'), code='avg'
            )
