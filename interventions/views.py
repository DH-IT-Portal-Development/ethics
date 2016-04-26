from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.views import CreateView, UpdateView, AllowErrorsMixin
from studies.models import Study
from studies.utils import get_study_progress

from .forms import InterventionForm
from .models import Intervention


#######################
# CRUD actions on Intervention
#######################
class InterventionMixin(object):
    """Mixin for an Intervention, to use in both InterventionCreate and InterventionUpdate below"""
    model = Intervention
    form_class = InterventionForm
    success_message = _('Interventie opgeslagen')

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(InterventionMixin, self).get_form_kwargs()
        kwargs['study'] = self.get_study()
        return kwargs

    def get_context_data(self, **kwargs):
        """Setting the Study and progress on the context"""
        context = super(InterventionMixin, self).get_context_data(**kwargs)
        study = self.get_study()
        context['study'] = study
        context['progress'] = get_study_progress(study) + 7
        return context

    def form_valid(self, form):
        """Sets the extra fields from the ModelForm on the Study"""
        study = self.get_study()
        study.has_observation = self.request.POST.get('has_observation', False)
        study.has_sessions = self.request.POST.get('has_sessions', False)
        study.save()
        return super(InterventionMixin, self).form_valid(form)

    def get_next_url(self):
        study = self.get_study()
        next_url = 'studies:session_end'
        pk = study.pk
        if study.has_observation:
            if hasattr(study, 'observation'):
                next_url = 'observations:update'
                pk = study.observation.pk
            else:
                next_url = 'observations:create'
        elif study.has_sessions:
            next_url = 'studies:session_start'
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        return reverse('studies:design', args=(self.get_study().pk,))

    def get_study(self):
        raise NotImplementedError


class InterventionCreate(InterventionMixin, AllowErrorsMixin, CreateView):
    """Creates a Intervention from a InterventionForm"""
    def form_valid(self, form):
        """Sets the Study on the Intervention before starting validation."""
        form.instance.study = self.get_study()
        return super(InterventionCreate, self).form_valid(form)

    def get_study(self):
        """Retrieves the Study from the pk kwarg"""
        return Study.objects.get(pk=self.kwargs['pk'])


class InterventionUpdate(InterventionMixin, AllowErrorsMixin, UpdateView):
    """Updates a Intervention from an InterventionForm"""
    def get_study(self):
        """Retrieves the Study from the form object"""
        return self.object.study
