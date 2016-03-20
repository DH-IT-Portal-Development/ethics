# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from core.views import CreateView, UpdateView

from ..models import Proposal, Wmo
from ..forms import WmoForm, WmoCheckForm
from ..utils import string_to_bool


#####################
# CRUD actions on WMO
#####################
class WmoMixin(object):
    model = Wmo
    form_class = WmoForm

    def get_next_url(self):
        wmo = self.object
        if wmo.status == Wmo.NO_WMO:
            proposal = wmo.proposal
            if hasattr(proposal, 'study'):
                return reverse('proposals:study_update', args=(proposal.pk,))
            else:
                return reverse('proposals:study_create', args=(proposal.pk,))
        elif wmo.status == Wmo.WAITING:
            return reverse('proposals:wmo_update', args=(wmo.pk,))
        else:
            return reverse('proposals:my_archive')

    def get_back_url(self):
        return reverse('proposals:update', args=(self.object.proposal.pk,))


class WmoCreate(WmoMixin, CreateView):
    success_message = _('WMO-gegevens opgeslagen')

    def form_valid(self, form):
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(WmoCreate, self).form_valid(form)


class WmoUpdate(WmoMixin, UpdateView):
    success_message = _('WMO-gegevens bewerkt')


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

    if is_metc is None or (not is_metc and (is_medical is None or is_behavioristic is None)):
        message = _('Neem contact op met Maartje de Klerk om de twijfels weg te nemen.')
        message_class = 'warning'
    elif is_metc or (is_medical and is_behavioristic):
        message = _('Uw studie zal moeten worden beoordeeld door de METC.')
        message_class = 'warning'

    return JsonResponse({'message': message, 'message_class': message_class})
