# -*- encoding: utf-8 -*-

from braces import views as braces
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView
from main.utils import string_to_bool
from proposals.models import Proposal
from interventions.models import Intervention
from observations.models import Observation

from ..forms import (
    StudyForm,
    StudyDesignForm,
    StudyConsentForm,
    StudyEndForm,
    StudyUpdateAttachmentsForm,
)
from ..models import Study, Documents
from ..utils import check_has_adults, check_necessity_required, get_study_progress
from ..mixins import StudyMixin


#######################
# CRUD actions on Study
#######################
class StudyUpdate(
    StudyMixin,
    AllowErrorsOnBackbuttonMixin,
    UpdateView,
):
    """Updates a Study from a StudyForm"""

    model = Study
    form_class = StudyForm
    success_message = _("Studie opgeslagen")

    def get_context_data(self, **kwargs):
        """Setting the progress on the context"""
        context = super(StudyUpdate, self).get_context_data(**kwargs)
        context["progress"] = get_study_progress(self.object)
        context["proposal"] = self.get_proposal()
        return context

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(StudyUpdate, self).get_form_kwargs()
        kwargs["proposal"] = self.object.proposal
        return kwargs

    def get_back_url(self):
        proposal = self.object.proposal
        if self.object.order == 1:
            return reverse("proposals:study_start", args=(proposal.pk,))
        else:
            prev = self.object.order - 1
            prev_study = Study.objects.get(proposal=proposal, order=prev)
            return reverse("studies:design_end", args=(prev_study.pk,))

    def get_next_url(self):
        """Continue to the Study design overview"""
        return reverse("studies:design", args=(self.object.pk,))


###############
# Other actions
###############
class StudyDesign(
    StudyMixin, AllowErrorsOnBackbuttonMixin, UpdateView, generic.edit.FormMixin
):
    model = Study
    form_class = StudyDesignForm
    success_message = _("Traject opgeslagen")
    template_name = "studies/study_design.html"

    def get_context_data(self, **kwargs):
        """Setting the progress on the context"""
        context = super(StudyDesign, self).get_context_data(**kwargs)
        context["progress"] = get_study_progress(self.object) + 3
        context["proposal"] = self.object.proposal
        return context

    def get_initial(self):
        """Fill in initial data"""

        study_types = ["has_intervention", "has_observation", "has_sessions"]

        initial = {
            "study_types": [
                study_type
                for study_type in study_types
                if getattr(self.object, study_type)
            ]
        }

        return initial

    def form_valid(self, form):
        """Fill in the model attributes, using the form data"""

        for study_type in form.fields["study_types"].choices:
            form_value = study_type[0] in form.data.getlist("study_types")
            form.instance.__setattr__(study_type[0], form_value)
        if not form.instance.has_intervention and hasattr(
            form.instance, "intervention"
        ):
            form.instance.intervention.delete()
        if not form.instance.has_observation and hasattr(form.instance, "observation"):
            form.instance.observation.delete()
        if not form.instance.has_sessions and form.instance.session_set.all():
            for session in form.instance.session_set.all():
                session.delete()
        form.instance.save()

        return super(StudyDesign, self).form_valid(form)

    def get_next_url(self):
        """
        Depending on whether this Study contains an Observation, Intervention or Session part,
        continue to this part. Otherwise, continue to the Study start overview.
        """
        study = self.object
        next_url = "studies:design_end"
        pk = study.pk
        if study.has_intervention:
            if hasattr(study, "intervention"):
                next_url = "interventions:update"
                pk = study.intervention.pk
            else:
                next_url = "interventions:create"
        elif study.has_observation:
            if hasattr(study, "observation"):
                next_url = "observations:update"
                pk = study.observation.pk
            else:
                next_url = "observations:create"
        elif study.has_sessions:
            next_url = "tasks:session_start"
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        """
        Return to the Study overview
        """
        return reverse("studies:update", args=(self.kwargs["pk"],))


class StudyEnd(
    StudyMixin,
    AllowErrorsOnBackbuttonMixin,
    UpdateView,
):
    """
    Completes a Study
    """

    model = Study
    form_class = StudyEndForm
    template_name = "studies/study_end.html"

    def get_context_data(self, **kwargs):
        """Setting the progress on the context"""
        context = super(StudyEnd, self).get_context_data(**kwargs)
        context["progress"] = get_study_progress(self.object, True) - 10
        context["proposal"] = self.object.proposal
        return context

    def get_next_url(self):
        """
        If there is another Study in this Proposal, continue to that one.
        Otherwise, go to the data management view.
        """
        proposal = self.object.proposal
        if self.object.order < proposal.studies_number:
            next_order = self.object.order + 1
            next_study = Study.objects.get(proposal=proposal, order=next_order)
            return reverse("studies:update", args=(next_study.pk,))
        else:
            return reverse("proposals:knowledge_security", args=(proposal.pk,))

    def get_back_url(self):
        study = self.object
        if study.has_sessions:
            next_url = "tasks:session_overview"
            pk = self.object.pk
        elif study.has_intervention:
            next_url = "interventions:update"
            pk = Intervention.objects.get(study=study).pk
        elif study.has_observation:
            next_url = "observations:update"
            pk = Observation.objects.get(study=study).pk
        else:
            next_url = "studies:design"
            pk = study.pk

        return reverse(next_url, args=(pk,))


class StudyUpdateAttachments(braces.GroupRequiredMixin, generic.UpdateView):
    """
    Allows the secretary to change the attachments on Study level
    """

    model = Documents
    template_name = "studies/study_update_attachments.html"
    form_class = StudyUpdateAttachmentsForm
    group_required = settings.GROUP_SECRETARY

    def form_valid(self, form):
        ret = super().form_valid(form)
        # Always regenerate the PDF after updating any study documents
        # This is necessary, as the canonical PDF protection might already
        # have kicked in if the secretary changes the documents later than
        # we initially expected.
        self.object.proposal.generate_pdf(force_overwrite=True)

        return ret

    def get_success_url(self):
        """Continue to the URL specified in the 'next' POST parameter"""
        return self.request.POST.get("next", "/")


################
# AJAX callbacks
################
@csrf_exempt
def has_adults(request):
    """
    This call checks whether the selected AgeGroups contain adult age groups.
    """
    age_groups = map(int, request.POST.getlist("age_groups[]"))
    return JsonResponse({"result": check_has_adults(age_groups)})


@csrf_exempt
def necessity_required(request):
    """
    This call checks whether the necessity questions are required. They are required when:
    * The researcher requires a supervisor AND one of these cases applies:
    ** A selected AgeGroup requires details.
    ** Participants have been selected on certain traits.
    ** Participants are legally incapable.
    """
    proposal = Proposal.objects.get(pk=request.POST.get("proposal_pk"))
    age_groups = map(int, request.POST.getlist("age_groups[]"))
    legally_incapable = string_to_bool(request.POST.get("legally_incapable"))
    return JsonResponse(
        {"result": check_necessity_required(proposal, age_groups, legally_incapable)}
    )
