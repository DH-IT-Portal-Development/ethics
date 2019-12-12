# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from core.models import YES, DOUBT
from core.views import CreateView, UpdateView, AllowErrorsOnBackbuttonMixin
from core.utils import get_secretary

from ..models import Proposal, Wmo
from ..forms import WmoForm, WmoApplicationForm, WmoCheckForm


#####################
# CRUD actions on WMO
#####################
class WmoMixin(AllowErrorsOnBackbuttonMixin, object):
    model = Wmo
    form_class = WmoForm

    def get_context_data(self, **kwargs):
        """Setting the Proposal on the context"""
        context = super(WmoMixin, self).get_context_data(**kwargs)
        context['proposal'] = self.get_proposal()
        return context

    def get_next_url(self):
        """
        If no Wmo is necessary, continue to definition of Study,
        else, start the Wmo application.
        """
        wmo = self.object
        if wmo.status == Wmo.NO_WMO:
            return reverse('proposals:study_start', args=(wmo.proposal.pk,))
        else:
            return reverse('proposals:wmo_application', args=(wmo.pk,))

    def get_back_url(self):
        """Return to the Proposal overview, or practice overview if we are in practice mode"""
        proposal = self.get_proposal()
        url = 'proposals:update_practice' if proposal.is_practice() else 'proposals:update'
        return reverse(url, args=(proposal.pk,))

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
class WmoApplication(UpdateView):
    model = Wmo
    form_class = WmoApplicationForm
    template_name = 'proposals/wmo_application.html'

    def get_context_data(self, **kwargs):
        """Setting the Proposal on the context"""
        context = super(WmoApplication, self).get_context_data(**kwargs)
        context['proposal'] = self.object.proposal
        return context

    def get_next_url(self):
        """Continue to the definition of a Study if we have completed the Wmo application"""
        wmo = self.object
        if wmo.status == Wmo.WAITING:
            return reverse('proposals:wmo_application', args=(wmo.pk,))
        else:
            return reverse('proposals:study_start', args=(wmo.proposal.pk,))

    def get_back_url(self):
        """Return to the Wmo overview"""
        return reverse('proposals:wmo_update', args=(self.object.pk,))


class WmoCheck(generic.FormView):
    form_class = WmoCheckForm
    template_name = 'proposals/wmo_check.html'


########################
# Preliminary assessment
########################
class PreAssessmentMixin(object):
    def get_next_url(self):
        """Different continue URL for pre-assessment Proposals"""
        return reverse('proposals:submit_pre', args=(self.object.proposal.pk,))

    def get_back_url(self):
        """Different return URL for pre-assessment Proposals"""
        return reverse('proposals:update_pre', args=(self.object.proposal.pk,))


class WmoCreatePreAssessment(PreAssessmentMixin, WmoCreate):
    pass


class WmoUpdatePreAssessment(PreAssessmentMixin, WmoUpdate):
    pass


################
# AJAX callbacks
################
@csrf_exempt
def check_wmo(request):
    """
    This call checks which WMO message should be generated.
    """
    is_metc = request.POST.get('metc') == YES
    is_medical = request.POST.get('medical') == YES
    is_behavioristic = request.POST.get('behavioristic') == YES

    doubt = request.POST.get('metc') == DOUBT or request.POST.get('medical') == DOUBT or request.POST.get('behavioristic') == DOUBT

    # Default message: OK.
    message = _('Uw studie hoeft niet te worden beoordeeld door de METC.')
    message_class = 'info'
    needs_metc = False

    # On doubt, contact secretary.
    if doubt:
        secretary = get_secretary().get_full_name()
        message = _('Neem contact op met {secretary} om de twijfels weg te nemen.').format(secretary=secretary)
        message_class = 'warning'
        needs_metc = True
    # Otherwise, METC review is necessary for METC studies (obviously) and
    # studies that have medical research questions or define user behavior
    elif is_metc or (is_medical and is_behavioristic):
        message = _('Uw studie zal moeten worden beoordeeld door de METC.')
        message_class = 'warning'
        needs_metc = True

    return JsonResponse({'needs_metc': needs_metc, 'message': message, 'message_class': message_class})
