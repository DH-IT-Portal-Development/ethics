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
            raise forms.ValidationError(_('Er bestaat al een aanvraag met deze '
                                          'titel.'), code='unique')


def AVGUnderstoodValidator(value):
# This does not seem to do anything, so I removed it from the model, however,
# if I try to remove this validator entirely I get an error when making
# migrations?
    if value is None:
        raise forms.ValidationError(
            _('Je dient deze vraag in te vullen om jouw aanvraag in '
              'te dienen'), code='avg'
            )
