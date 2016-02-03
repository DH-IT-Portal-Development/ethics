# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from .base_views import UpdateView, DeleteView, get_session_progress
from ..forms import SessionStartForm, TaskStartForm, TaskEndForm, SessionEndForm
from ..mixins import AllowErrorsMixin
from ..models import Proposal, Session, Task


######################
# Actions on a Session
######################
class ProposalSessionStart(AllowErrorsMixin, UpdateView):
    """Initial creation of Sessions"""
    model = Proposal
    form_class = SessionStartForm
    template_name = 'proposals/session_start.html'
    success_message = _('%(sessions_number)s sessie(s) voor aanvraag %(title)s aangemaakt')

    def form_valid(self, form):
        """Creates or deletes Sessions on save"""
        nr_sessions = form.cleaned_data['sessions_number']
        proposal = form.instance
        current = proposal.session_set.count() or 0

        # Create sessions
        for n in xrange(current, nr_sessions):
            order = n + 1
            session = Session(proposal=proposal, order=order)
            session.save()

        # Delete sessions
        for n in xrange(nr_sessions, current):
            order = n + 1
            session = Session.objects.get(proposal=proposal, order=order)
            session.delete()

        # If the number of Sessions has changed, invalidate the Proposal fields
        if current != nr_sessions:
            proposal.sessions_duration = None
            proposal.sessions_stressful = None
            proposal.sessions_stressful_details = ''
            proposal.save()

        return super(ProposalSessionStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('proposals:task_start', args=(self.object.first_session().id,))

    def get_back_url(self):
        return reverse('proposals:study_update', args=(self.object.id,))

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, title=self.object.title)


def add_session(request, pk):
    """Adds a Session to the given Proposal"""
    proposal = get_object_or_404(Proposal, pk=pk)
    new_session_number = proposal.sessions_number + 1

    proposal.sessions_number = new_session_number
    proposal.save()

    session = Session(proposal=proposal, order=new_session_number)
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_start', args=(session.id,)))


class ProposalSessionEnd(AllowErrorsMixin, UpdateView):
    """
    Completes the creation of Sessions
    """
    model = Proposal
    form_class = SessionEndForm
    template_name = 'proposals/session_end.html'
    success_message = _(u'Sessies toevoegen beëindigd')

    def get_initial(self):
        """If there is only one Session, transfer the data to Proposal level"""
        if self.object.sessions_number == 1:
            session = self.object.first_session()
            return {'sessions_stressful': session.tasks_stressful,
                    'sessions_stressful_details': session.tasks_stressful_details}
        else:
            return super(ProposalSessionEnd, self).get_initial()

    def get_next_url(self):
        return reverse('proposals:study_survey', args=(self.object.id,))

    def get_back_url(self):
        return reverse('proposals:task_end', args=(self.object.last_session().id,))


class SessionDelete(DeleteView):
    model = Session
    success_message = _('Sessie verwijderd')

    def get_success_url(self):
        return reverse('proposals:detail', args=(self.object.proposal.id,))

    def delete(self, request, *args, **kwargs):
        """
        Deletes the Session and updates the Proposal and other Sessions.
        Completely overrides the default delete function (as that calls delete too late for us).
        TODO: maybe save the HttpResponseRedirect and then perform the other actions?
        """
        self.object = self.get_object()
        order = self.object.order
        proposal = self.object.proposal
        success_url = self.get_success_url()
        self.object.delete()

        # If the session number is lower than the total number of sessions (e.g. 3 of 4),
        # set the other session numbers one lower
        for s in Session.objects.filter(proposal=proposal, order__gt=order):
            s.order -= 1
            s.save()

        # Set the number of sessions on Proposal
        proposal.sessions_number -= 1
        proposal.save()

        return HttpResponseRedirect(success_url)


class TaskStart(AllowErrorsMixin, UpdateView):
    """Initially sets the total number of Tasks for a Session"""
    model = Session
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_message = _('%(tasks_number)s ta(a)k(en) aangemaakt')

    def get_context_data(self, **kwargs):
        context = super(TaskStart, self).get_context_data(**kwargs)
        context['progress'] = get_session_progress(self.object)
        return context

    def form_valid(self, form):
        """Creates or deletes Tasks on save"""
        nr_tasks = form.cleaned_data['tasks_number']
        session = form.instance
        current = session.task_set.count() or 0

        # Create Tasks
        for n in xrange(current, nr_tasks):
            order = n + 1
            task = Task(session=session, order=order)
            task.save()

        # Delete Tasks
        for n in xrange(nr_tasks, current):
            order = n + 1
            task = Task.objects.get(session=session, order=order)
            task.delete()

        # If the number of Tasks has changed, invalidate the Session and Proposal fields
        if current != nr_tasks:
            session.tasks_duration = None
            session.tasks_stressful = None
            session.tasks_stressful_details = ''
            session.save()

            proposal = session.proposal
            proposal.sessions_duration = None
            proposal.sessions_stressful = None
            proposal.sessions_stressful_details = ''
            proposal.save()

        return super(TaskStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('proposals:task_update', args=(self.object.first_task().id,))

    def get_back_url(self):
        try:
            # Try to return to task_end of the previous Session
            prev_session = Session.objects.get(proposal=self.object.proposal, order=self.object.order - 1)
            return reverse('proposals:task_end', args=(prev_session.id,))
        except Session.DoesNotExist:
            # If this is the first Session, return to session_start
            return reverse('proposals:session_start', args=(self.object.proposal.id,))


def add_task(request, pk):
    """Updates the tasks_number on a Session"""
    # TODO: fix this or delete functionality.
    session = get_object_or_404(Session, pk=pk)
    session.tasks_number += 1
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_create', args=(session.id,)))


class TaskEnd(AllowErrorsMixin, UpdateView):
    """Completes a Session"""
    model = Session
    form_class = TaskEndForm
    template_name = 'proposals/task_end.html'
    success_message = _(u'Taken toevoegen beëindigd')

    def get_context_data(self, **kwargs):
        context = super(TaskEnd, self).get_context_data(**kwargs)
        context['progress'] = get_session_progress(self.object, True)
        return context

    def get_next_url(self):
        try:
            # Try to continue to next Session
            next_session = Session.objects.get(proposal=self.object.proposal, order=self.object.order + 1)
            return reverse('proposals:task_start', args=(next_session.id,))
        except Session.DoesNotExist:
            # If this is the last Session, continue to session_end
            return reverse('proposals:session_end', args=(self.object.proposal.id,))

    def get_back_url(self):
        return reverse('proposals:task_update', args=(self.object.last_task().id,))