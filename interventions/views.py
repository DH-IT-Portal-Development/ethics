from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.views import CreateView, UpdateView, AllowErrorsMixin
from studies.models import Study

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

    def get_next_url(self):
        study = self.object.study
        next_url = 'studies:session_end'
        pk = study.pk
        if study.has_sessions:
            next_url = 'studies:session_start'
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        study = self.object.study if self.object else Study.objects.get(pk=self.kwargs['pk'])
        pk = study.pk
        next_url = 'studies:design'
        if study.has_observation:
            next_url = 'observations:update'
            pk = study.observation.pk
        return reverse(next_url, args=(pk,))


class InterventionCreate(InterventionMixin, AllowErrorsMixin, CreateView):
    """Creates a Intervention from a InterventionForm"""

    def get_context_data(self, **kwargs):
        """Setting the Study on the context"""
        context = super(InterventionCreate, self).get_context_data(**kwargs)
        context['study'] = Study.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """Sets the Study on the Intervention before starting validation."""
        form.instance.study = Study.objects.get(pk=self.kwargs['pk'])
        return super(InterventionCreate, self).form_valid(form)


class InterventionUpdate(InterventionMixin, AllowErrorsMixin, UpdateView):
    """Updates a Intervention from an InterventionForm"""

    def get_context_data(self, **kwargs):
        """Setting the Study on the context"""
        context = super(InterventionUpdate, self).get_context_data(**kwargs)
        context['study'] = self.object.study
        return context
