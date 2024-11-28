from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from main.views import CreateView, UpdateView, AllowErrorsOnBackbuttonMixin
from fetc import settings
from studies.utils import get_study_progress
from studies.mixins import StudyFromURLMixin
from proposals.mixins import StepperContextMixin

from .forms import ObservationForm, ObservationUpdateAttachmentsForm
from .models import Observation


#############################
# CRUD actions on Observation
#############################
class ObservationMixin(StepperContextMixin):
    """Mixin for a Observation, to use in both ObservationCreate and ObservationUpdate below"""

    model = Observation
    form_class = ObservationForm
    success_message = _("Observatie opgeslagen")

    def get_context_data(self, **kwargs):
        """Setting the Study and progress on the context"""
        context = super(ObservationMixin, self).get_context_data(**kwargs)
        study = self.get_study()
        context["study"] = study
        context["proposal"] = study.proposal
        context["progress"] = get_study_progress(study) + 5
        return context

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(ObservationMixin, self).get_form_kwargs()
        kwargs["study"] = self.get_study()
        return kwargs

    def get_next_url(self):
        study = self.get_study()
        next_url = "studies:design_end"
        pk = study.pk
        if study.has_sessions:
            next_url = "tasks:session_start"
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        study = self.get_study()
        pk = study.pk
        next_url = "studies:design"
        if study.get_intervention():
            next_url = "interventions:update"
            pk = study.intervention.pk
        return reverse(next_url, args=(pk,))

    def get_study(self):
        # Um.... what?
        raise NotImplementedError

    def get_proposal(self):
        return self.get_object().study.proposal


class AttachmentsUpdate(UpdateView):
    model = Observation
    template_name = "observations/observation_update_attachments.html"
    form_class = ObservationUpdateAttachmentsForm
    group_required = settings.GROUP_SECRETARY


class ObservationCreate(
    StudyFromURLMixin,
    ObservationMixin,
    AllowErrorsOnBackbuttonMixin,
    CreateView,
):
    """Creates an Observation from a ObservationForm"""

    def form_valid(self, form):
        """Sets the Study on the Observation before starting validation."""
        form.instance.study = self.get_study()
        return super(ObservationCreate, self).form_valid(form)


class ObservationUpdate(ObservationMixin, AllowErrorsOnBackbuttonMixin, UpdateView):
    """Updates a Observation from a ObservationForm"""

    def get_study(self):
        """Retrieves the Study from the form object"""
        return self.object.study
