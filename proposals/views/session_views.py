# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.views import AllowErrorsMixin, UpdateView
from observations.models import Observation
from interventions.models import Intervention
from tasks.models import Session

from ..forms import SessionStartForm, SessionEndForm
from ..models import Study


######################
# Actions on a Session
######################
class SessionStart(AllowErrorsMixin, UpdateView):
    """Initial creation of Sessions"""
    model = Study
    form_class = SessionStartForm
    template_name = 'proposals/session_start.html'
    success_message = _('%(sessions_number)s sessie(s) voor studie %(title)s aangemaakt')

    def form_valid(self, form):
        """Creates or deletes Sessions on save"""
        nr_sessions = form.cleaned_data['sessions_number']
        study = form.instance
        current = study.session_set.count() or 0

        # Create sessions
        for n in xrange(current, nr_sessions):
            order = n + 1
            session = Session(study=study, order=order)
            session.save()

        # Delete sessions
        for n in xrange(nr_sessions, current):
            order = n + 1
            session = Session.objects.get(study=study, order=order)
            session.delete()

        # If the number of Sessions has changed, invalidate the Study fields
        if current != nr_sessions:
            study.sessions_duration = None
            study.save()

        return super(SessionStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('tasks:start', args=(self.object.first_session().pk,))

    def get_back_url(self):
        study = self.object
        next_url = 'proposals:study_design'
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
    template_name = 'proposals/session_end.html'
    success_message = _(u'Sessies toevoegen beëindigd')

    def get_initial(self):
        """
        - If there is only one Session, transfer the duration to Study level
        - If there are no Sessions, set the duration to zero
        """
        initial = super(SessionEnd, self).get_initial()
        study = self.object
        if not study.has_sessions:
            initial['sessions_duration'] = 0
        elif study.sessions_number == 1:
            initial['sessions_duration'] = study.first_session().tasks_duration
        return initial

    def get_next_url(self):
        return reverse('proposals:study_survey', args=(self.object.pk,))

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
            next_url = 'proposals:study_design'
            pk = study.pk

        return reverse(next_url, args=(pk,))
