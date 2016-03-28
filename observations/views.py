from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from braces.views import LoginRequiredMixin
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from core.views import UserAllowedMixin, success_url

from .forms import ObservationForm, LocationsInline
from .models import Study, Observation


#############################
# CRUD actions on Observation
#############################
# NOTE: below mixin is non-standard, as it include inlines
# NOTE: no success message will be generated: https://github.com/AndrewIngram/django-extra-views/issues/59
class ObservationMixin(object):
    """Mixin for a Observation, to use in both ObservationCreate and ObservationUpdate below"""
    model = Observation
    form_class = ObservationForm
    success_message = _('Observatie opgeslagen')
    inlines = [LocationsInline]

    def get_success_url(self):
        return success_url(self)

    def get_next_url(self):
        study = self.object.study
        next_url = 'proposals:session_end'
        pk = study.pk
        if study.has_intervention:
            if hasattr(study, 'intervention'):
                next_url = 'interventions:update'
                pk = study.intervention.pk
            else:
                next_url = 'interventions:create'
        elif study.has_sessions:
            next_url = 'proposals:session_start'
        return reverse(next_url, args=(pk,))

    def forms_invalid(self, form, inlines):
        """
        On back button, allow form to have errors.
        """
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(ObservationMixin, self).forms_invalid(form, inlines)


class ObservationCreate(LoginRequiredMixin, ObservationMixin,
                        UserAllowedMixin, CreateWithInlinesView):
    """Creates an Observation from a ObservationForm"""
    def forms_valid(self, form, inlines):
        """Sets the Study on the Observation before starting validation."""
        form.instance.study = Study.objects.get(pk=self.kwargs['pk'])
        return super(ObservationCreate, self).forms_valid(form, inlines)

    def get_back_url(self):
        return reverse('proposals:study_design', args=(self.kwargs['pk'],))


class ObservationUpdate(LoginRequiredMixin, ObservationMixin,
                        UserAllowedMixin, UpdateWithInlinesView):
    """Updates a Observation from a ObservationForm"""
    def get_back_url(self):
        return reverse('proposals:study_design', args=(self.object.study.pk,))
