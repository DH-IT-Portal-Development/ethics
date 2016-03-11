from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from .base_views import CreateView, UpdateView
from ..mixins import AllowErrorsMixin
from ..forms import InterventionForm
from ..models import Study, Intervention


#######################
# CRUD actions on Intervention
#######################
class InterventionMixin(object):
    """Mixin for an Intervention, to use in both InterventionCreate and InterventionUpdate below"""
    model = Intervention
    form_class = InterventionForm
    success_message = _('Interventie opgeslagen')

    def get_next_url(self):
        return reverse('proposals:session_start', args=(self.object.proposal.id,))

    def get_back_url(self):
        return reverse('proposals:observation_update', args=(self.kwargs['pk'],))


class InterventionCreate(InterventionMixin, AllowErrorsMixin, CreateView):
    """Creates a Intervention from a InterventionForm"""

    def form_valid(self, form):
        """Sets the Study on the Intervention before starting validation."""
        form.instance.study = Study.objects.get(pk=self.kwargs['pk'])
        return super(InterventionCreate, self).form_valid(form)


class InterventionUpdate(InterventionMixin, AllowErrorsMixin, UpdateView):
    """Updates a Intervention from an InterventionForm"""
