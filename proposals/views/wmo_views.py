# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _

from main.models import YesNoDoubt
from main.views import CreateView, UpdateView, AllowErrorsOnBackbuttonMixin
from main.utils import get_secretary
from proposals.mixins import StepperContextMixin

from ..models import Proposal, Wmo
from ..forms import WmoForm, WmoApplicationForm


#####################
# CRUD actions on WMO
#####################
class WmoMixin(AllowErrorsOnBackbuttonMixin, object):
    model = Wmo
    form_class = WmoForm

    def get_context_data(self, **kwargs):
        """Setting the Proposal on the context"""
        context = super(WmoMixin, self).get_context_data(**kwargs)
        context["proposal"] = self.get_proposal()
        return context

    def get_next_url(self):
        """
        If no Wmo is necessary, continue to definition of Study,
        else, start the Wmo application.
        """
        wmo = self.object
        if wmo.status == Wmo.WMOStatuses.NO_WMO:
            return reverse("proposals:study_start", args=(wmo.proposal.pk,))
        else:
            return reverse("proposals:wmo_application", args=(wmo.pk,))

    def get_back_url(self):
        """Return to the Proposal overview, or practice overview if we are in practice mode"""
        proposal = self.get_proposal()
        url = (
            "proposals:pre_approved"
            if proposal.is_pre_approved
            else "proposals:research_goal"
        )
        return reverse(url, args=(proposal.pk,))

    def get_proposal(self):
        raise NotImplementedError


class WmoCreate(
    StepperContextMixin,
    WmoMixin,
    CreateView,
):
    success_message = _("WMO-gegevens opgeslagen")

    def form_valid(self, form):
        """Saves the Proposal on the WMO instance"""
        form.instance.proposal = self.get_proposal()
        return super(WmoCreate, self).form_valid(form)

    def get_proposal(self):
        """Retrieves the Proposal from the pk kwarg"""
        return Proposal.objects.get(pk=self.kwargs["pk"])


class WmoUpdate(
    StepperContextMixin,
    WmoMixin,
    UpdateView,
):
    success_message = _("WMO-gegevens bewerkt")

    def get_proposal(self):
        """Retrieves the Proposal from the form object"""
        return self.object.proposal


######################
# Other actions on WMO
######################
class WmoApplication(
    UpdateView,
    StepperContextMixin,
):
    model = Wmo
    form_class = WmoApplicationForm
    template_name = "proposals/wmo_application.html"

    def get_context_data(self, **kwargs):
        """Setting the Proposal on the context"""
        context = super(WmoApplication, self).get_context_data(**kwargs)
        context["proposal"] = self.object.proposal
        return context

    def get_next_url(self):
        """Continue to the definition of a Study if we have completed the Wmo application"""
        wmo = self.object
        if wmo.status == Wmo.WMOStatuses.WAITING:
            return reverse("proposals:wmo_application", args=(wmo.pk,))
        else:
            return reverse("proposals:study_start", args=(wmo.proposal.pk,))

    def get_back_url(self):
        """Return to the Wmo overview"""
        return reverse("proposals:wmo_update", args=(self.object.pk,))


########################
# Preliminary assessment
########################
class PreAssessmentMixin(object):
    def get_next_url(self):
        """Different continue URL for pre-assessment Proposals"""
        wmo = self.object
        if wmo.status == Wmo.WMOStatuses.NO_WMO:
            return reverse("proposals:submit_pre", args=(self.object.proposal.pk,))
        else:
            return reverse("proposals:wmo_application_pre", args=(wmo.pk,))

    def get_back_url(self):
        """Different return URL for pre-assessment Proposals"""
        return reverse("proposals:update", args=(self.object.proposal.pk,))


class WmoCreatePreAssessment(PreAssessmentMixin, WmoCreate):
    pass


class WmoUpdatePreAssessment(PreAssessmentMixin, WmoUpdate):
    pass


class WmoApplicationPreAssessment(PreAssessmentMixin, WmoApplication):
    def get_next_url(self):
        """Different continue URL for pre-assessment Proposals"""
        return reverse("proposals:submit_pre", args=(self.object.proposal.pk,))


################
# AJAX callbacks
################
@csrf_exempt
def check_wmo(request):
    """
    This call checks which WMO message should be generated.
    """
    is_metc = request.POST.get("metc") == YesNoDoubt.YES
    is_medical = request.POST.get("medical") == YesNoDoubt.YES

    doubt = (
        request.POST.get("metc") == YesNoDoubt.DOUBT
        or request.POST.get("medical") == YesNoDoubt.DOUBT
    )

    # Default message: OK.
    message = _("Je onderzoek hoeft niet te worden beoordeeld door de METC.")
    message_class = "info"
    needs_metc = False

    # On doubt, contact secretary.
    if doubt:
        secretary = get_secretary()
        message = _(
            'Neem contact op met <a href="{link}">{secretary}</a> om de twijfels weg te nemen.'
        ).format(link="mailto:" + secretary.email, secretary=secretary.get_full_name())
        message_class = "warning"
        needs_metc = True
    # Otherwise, METC review is necessary for METC studies (obviously) and
    # studies that have medical research questions or define user behavior
    elif is_metc or is_medical:
        message = _("Je onderzoek zal moeten worden beoordeeld door de METC.")
        message_class = "warning"
        needs_metc = True

    return JsonResponse(
        {"needs_metc": needs_metc, "message": message, "message_class": message_class}
    )
