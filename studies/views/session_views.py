# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.views import AllowErrorsMixin, UpdateView
from observations.models import Observation
from interventions.models import Intervention
from tasks.models import Session

from ..forms import SessionStartForm, SessionEndForm
from ..models import Study
from ..utils import get_study_progress


######################
# Actions on a Session
######################
class SessionStart(AllowErrorsMixin, UpdateView):
    """Initial creation of Sessions"""
    model = Study
    form_class = SessionStartForm
    template_name = 'studies/session_start.html'
    success_message = _('%(sessions_number)s sessie(s) voor studie %(title)s aangemaakt')

    def get_context_data(self, **kwargs):
        """Setting the progress on the context"""
        context = super(SessionStart, self).get_context_data(**kwargs)
        context['progress'] = get_study_progress(self.object) + 9
        return context

    def form_valid(self, form):
        """Creates or deletes Sessions on save"""
        nr_sessions = form.cleaned_data['sessions_number']
        study = form.instance
        current = study.session_set.count() or 0

        # Create Sessions
        for n in xrange(current, nr_sessions):
            order = n + 1
            session = Session(study=study, order=order)
            session.save()

        # Delete Sessions
        for n in xrange(nr_sessions, current):
            order = n + 1
            session = Session.objects.get(study=study, order=order)
            session.delete()

        return super(SessionStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('tasks:start', args=(self.object.first_session().pk,))

    def get_back_url(self):
        study = self.object
        next_url = 'studies:design'
        pk = study.pk
        if study.has_intervention:
            next_url = 'interventions:update'
            pk = study.intervention.pk
        elif study.has_observation:
            next_url = 'observations:update'
            pk = study.observation.pk
        return reverse(next_url, args=(pk,))

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, title=self.object.proposal.title)


class SessionEnd(AllowErrorsMixin, UpdateView):
    """
    Completes the creation of Sessions
    """
    model = Study
    form_class = SessionEndForm
    template_name = 'studies/session_end.html'
    success_message = _(u'Sessies toevoegen beëindigd')

    def get_context_data(self, **kwargs):
        """Setting the progress on the context"""
        context = super(SessionEnd, self).get_context_data(**kwargs)
        context['progress'] = get_study_progress(self.object, True) - 5
        return context

    def get_next_url(self):
        return reverse('studies:consent', args=(self.object.pk,))

    def get_back_url(self):
        study = self.object
        if study.has_sessions:
            next_url = 'tasks:end'
            pk = self.object.last_session().pk
        elif study.has_intervention:
            next_url = 'interventions:update'
            pk = Intervention.objects.get(study=study).pk
        elif study.has_observation:
            next_url = 'observations:update'
            pk = Observation.objects.get(study=study).pk
        else:
            next_url = 'studies:design'
            pk = study.pk

        return reverse(next_url, args=(pk,))
