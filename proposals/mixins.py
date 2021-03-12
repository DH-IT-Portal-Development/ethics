from braces.views import UserFormKwargsMixin
from .models import Proposal
from .forms import ProposalForm
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _



class ProposalMixin(UserFormKwargsMixin):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Studie %(title)s bewerkt')

    def get_next_url(self):
        """If the Proposal has a Wmo model attached, go to update, else, go to create"""
        proposal = self.object
        if hasattr(proposal, 'wmo'):
            return reverse('proposals:wmo_update', args=(proposal.pk,))
        else:
            return reverse('proposals:wmo_create', args=(proposal.pk,))



class ProposalContextMixin:
        
    def get_context_data(self, **kwargs):
        context = super(ProposalContextMixin, self).get_context_data(**kwargs)
        context['is_supervisor'] = self.object.supervisor == self.request.user
        context['is_practice'] = self.object.is_practice()
        return context
