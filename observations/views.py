from django.urls import reverse
from django.utils.translation import ugettext as _

from core.views import CreateView, UpdateView, AllowErrorsOnBackbuttonMixin
from etcl import settings
from studies.models import Study
from studies.utils import get_study_progress

from .forms import ObservationForm, ObservationUpdateAttachmentsForm
from .models import Observation


#############################
# CRUD actions on Observation
#############################
class ObservationMixin(object):
    """Mixin for a Observation, to use in both ObservationCreate and ObservationUpdate below"""
    model = Observation
    form_class = ObservationForm
    success_message = _('Observatie opgeslagen')

    def get_context_data(self, **kwargs):
        """Setting the Study and progress on the context"""
        context = super(ObservationMixin, self).get_context_data(**kwargs)
        study = self.get_study()
        context['study'] = study
        context['progress'] = get_study_progress(study) + 5
        return context

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(ObservationMixin, self).get_form_kwargs()
        kwargs['study'] = self.get_study()
        return kwargs

    def get_next_url(self):
        study = self.get_study()
        next_url = 'studies:design_end'
        pk = study.pk
        if study.has_sessions:
            next_url = 'studies:session_start'
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        study = self.get_study()
        pk = study.pk
        next_url = 'studies:design'
        if study.has_intervention:
            next_url = 'interventions:update'
            pk = study.intervention.pk
        return reverse(next_url, args=(pk,))

    def get_study(self):
        raise NotImplementedError


class AttachmentsUpdate(UpdateView):
    model = Observation
    template_name = 'observations/observation_update_attachments.html'
    form_class = ObservationUpdateAttachmentsForm
    group_required = settings.GROUP_SECRETARY


class ObservationCreate(ObservationMixin, AllowErrorsOnBackbuttonMixin, CreateView):
    """Creates an Observation from a ObservationForm"""

    def form_valid(self, form):
        """Sets the Study on the Observation before starting validation."""
        form.instance.study = self.get_study()
        return super(ObservationCreate, self).form_valid(form)

    def get_study(self):
        """Retrieves the Study from the pk kwarg"""
        return Study.objects.get(pk=self.kwargs['pk'])


class ObservationUpdate(ObservationMixin, AllowErrorsOnBackbuttonMixin, UpdateView):
    """Updates a Observation from a ObservationForm"""

    def get_study(self):
        """Retrieves the Study from the form object"""
        return self.object.study
