# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from core.views import CreateView, UpdateView
from core.utils import get_secretary, string_to_bool

from ..models import Proposal, Wmo
from ..forms import WmoForm, WmoCheckForm


#####################
# CRUD actions on WMO
#####################
class WmoMixin(object):
    model = Wmo
    form_class = WmoForm

    def get_context_data(self, **kwargs):
        """Setting the Proposal on the context"""
        context = super(WmoMixin, self).get_context_data(**kwargs)
        context['proposal'] = self.get_proposal()
        return context

    def get_next_url(self):
        wmo = self.object
        if wmo.status == Wmo.NO_WMO:
            proposal = wmo.proposal
            return reverse('proposals:study_start', args=(proposal.pk,))
        elif wmo.status == Wmo.WAITING:
            return reverse('proposals:wmo_update', args=(wmo.pk,))
        else:
            return reverse('proposals:my_archive')

    def get_back_url(self):
        return reverse('proposals:update', args=(self.object.proposal.pk,))

    def get_proposal(self):
        raise NotImplementedError


class WmoCreate(WmoMixin, CreateView):
    success_message = _('WMO-gegevens opgeslagen')

    def form_valid(self, form):
        """Saves the Proposal on the WMO instance"""
        form.instance.proposal = self.get_proposal()
        return super(WmoCreate, self).form_valid(form)

    def get_proposal(self):
        """Retrieves the Proposal from the pk kwarg"""
        return Proposal.objects.get(pk=self.kwargs['pk'])


class WmoUpdate(WmoMixin, UpdateView):
    success_message = _('WMO-gegevens bewerkt')

    def get_proposal(self):
        """Retrieves the Proposal from the form object"""
        return self.object.proposal


######################
# Other actions on WMO
######################
class WmoCheck(generic.FormView):
    form_class = WmoCheckForm
    template_name = 'proposals/wmo_check.html'


################
# AJAX callbacks
################
@csrf_exempt
def check_wmo(request):
    """
    This call checks which WMO message should be generated.
    """
    is_metc = string_to_bool(request.POST.get('metc'))
    is_medical = string_to_bool(request.POST.get('medical'))
    is_behavioristic = string_to_bool(request.POST.get('behavioristic'))

    # Default message: OK.
    message = _('Uw studie hoeft niet te worden beoordeeld door de METC.')
    message_class = 'info'
    needs_metc = False

    if is_metc is None or (not is_metc and (is_medical is None or is_behavioristic is None)):
        secretary = get_secretary().get_full_name()
        message = _('Neem contact op met {secretary} om de twijfels weg te nemen.').format(secretary=secretary)
        message_class = 'warning'
        needs_metc = True
    elif is_metc or (is_medical and is_behavioristic):
        message = _('Uw studie zal moeten worden beoordeeld door de METC.')
        message_class = 'warning'
        needs_metc = True

    return JsonResponse({'needs_metc': needs_metc, 'message': message, 'message_class': message_class})
