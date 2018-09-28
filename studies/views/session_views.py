# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import ugettext as _

from core.views import AllowErrorsMixin, UpdateView
from tasks.models import Session

from ..forms import SessionStartForm
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
        for n in range(current, nr_sessions):
            order = n + 1
            session = Session(study=study, order=order)
            session.save()

        # Delete Sessions
        for n in range(nr_sessions, current):
            order = n + 1
            session = Session.objects.get(study=study, order=order)
            session.delete()

        return super(SessionStart, self).form_valid(form)

    def get_next_url(self):
        """Continue to the addition of Tasks"""
        return reverse('tasks:start', args=(self.object.first_session().pk,))

    def get_back_url(self):
        """
        Depending on whether this Study contains an Observation or Intervention part,
        return to this part. Otherwise, return to the Study design overview.
        """
        study = self.object
        next_url = 'studies:design'
        pk = study.pk
        if study.has_observation:
            next_url = 'observations:update'
            pk = study.observation.pk
        elif study.has_intervention:
            next_url = 'interventions:update'
            pk = study.intervention.pk
        return reverse(next_url, args=(pk,))

    def get_success_message(self, cleaned_data):
        """Fill the success message using the cleaned_data"""
        return self.success_message % dict(cleaned_data, title=self.object.proposal.title)
