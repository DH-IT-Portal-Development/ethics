# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from .base_views import UpdateView, DeleteView, get_session_progress
from ..copy import copy_tasks_to_session
from ..forms import SessionStartForm, TaskStartForm, TaskEndForm, SessionEndForm
from ..mixins import AllowErrorsMixin, DeletionAllowedMixin
from ..models import Study, Session, Task, Observation, Intervention


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
        return reverse('proposals:task_start', args=(self.object.first_session().pk,))

    def get_back_url(self):
        study = self.object
        next_url = 'proposals:study_design'
        pk = study.pk
        if study.has_intervention:
            next_url = 'proposals:intervention_update'
            pk = study.intervention.pk
        elif study.has_observation:
            next_url = 'proposals:observation_update'
            pk = study.observation.pk
        return reverse(next_url, args=(pk,))

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, title=self.object.proposal.title)


def add_session(request, pk):
    """Adds a Session to the given Study"""
    study = get_object_or_404(Study, pk=pk)
    new_session_number = study.sessions_number + 1

    study.sessions_number = new_session_number
    study.save()

    session = Session(study=study, order=new_session_number)
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_start', args=(session.pk,)))


class SessionEnd(AllowErrorsMixin, UpdateView):
    """
    Completes the creation of Sessions
    """
    model = Study
    form_class = SessionEndForm
    template_name = 'proposals/session_end.html'
    success_message = _(u'Sessies toevoegen beëindigd')

    def get_initial(self):
        """If there is only one Session, transfer the duration to Study level"""
        initial = super(SessionEnd, self).get_initial()
        if self.object.sessions_number == 1:
            session = self.object.first_session()
            initial['sessions_duration'] = session.tasks_duration
        return initial

    def get_next_url(self):
        return reverse('proposals:study_survey', args=(self.object.pk,))

    def get_back_url(self):
        study = self.object
        if study.has_sessions:
            next_url = 'proposals:task_end'
            pk = self.object.last_session().pk
        elif study.has_intervention:
            next_url = 'proposals:intervention_update'
            pk = Intervention.objects.get(study=study).pk
        else:
            next_url = 'proposals:observation_update'
            pk = Observation.objects.get(study=study).pk

        return reverse(next_url, args=(pk,))


class SessionDelete(DeletionAllowedMixin, DeleteView):
    model = Session
    success_message = _('Sessie verwijderd')

    def get_success_url(self):
        return reverse('proposals:session_end', args=(self.object.study.pk,))

    def delete(self, request, *args, **kwargs):
        """
        Deletes the Session and updates the Study and other Sessions.
        Completely overrides the default delete function (as that calls delete too late for us).
        """
        self.object = self.get_object()
        order = self.object.order
        study = self.object.study
        success_url = self.get_success_url()
        self.object.delete()

        # If the order is lower than the total number of Sessions (e.g. 3 of 4), set the other orders one lower
        for s in Session.objects.filter(study=study, order__gt=order):
            s.order -= 1
            s.save()

        # Set the number of Sessions on Study
        study.sessions_number -= 1
        study.save()

        return HttpResponseRedirect(success_url)


class TaskStart(AllowErrorsMixin, UpdateView):
    """Initial creation of Tasks for a Session"""
    model = Session
    form_class = TaskStartForm
    template_name = 'proposals/task_start.html'
    success_message = _('%(tasks_number)s ta(a)k(en) aangemaakt')

    def get_context_data(self, **kwargs):
        context = super(TaskStart, self).get_context_data(**kwargs)
        context['progress'] = get_session_progress(self.object)
        return context

    def form_valid(self, form):
        """Copies, creates or deletes Tasks on save"""
        if 'is_copy' in form.cleaned_data and form.cleaned_data['is_copy']:
            session = form.instance

            # Delete all existing Tasks
            for task in session.task_set.all():
                task.delete()

            # Copy fields from the parent Session
            s = form.cleaned_data['parent_session']
            session.tasks_number = s.tasks_number
            session.tasks_duration = s.tasks_duration
            session.save()

            # Update cleaned_data as well, to make sure this isn't overridden on the super call below
            form.cleaned_data['tasks_number'] = s.tasks_number

            # Copy Tasks from the parent Session
            copy_tasks_to_session(session, s.task_set.all())
        else:
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

            # If the number of Tasks has changed, invalidate the Session and Study duration
            if current != nr_tasks:
                session.tasks_duration = None
                session.save()

                study = session.study
                study.sessions_duration = None
                study.save()

        return super(TaskStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('proposals:task_update', args=(self.object.first_task().pk,))

    def get_back_url(self):
        try:
            # Try to return to task_end of the previous Session
            prev_session = Session.objects.get(study=self.object.study, order=self.object.order - 1)
            return reverse('proposals:task_end', args=(prev_session.pk,))
        except Session.DoesNotExist:
            # If this is the first Session, return to session_start
            return reverse('proposals:session_start', args=(self.object.study.pk,))


def add_task(request, pk):
    """Updates the tasks_number on a Session"""
    # TODO: fix this or delete functionality.
    session = get_object_or_404(Session, pk=pk)
    session.tasks_number += 1
    session.save()

    return HttpResponseRedirect(reverse('proposals:task_create', args=(session.pk,)))


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
            next_session = Session.objects.get(study=self.object.study, order=self.object.order + 1)
            return reverse('proposals:task_start', args=(next_session.pk,))
        except Session.DoesNotExist:
            # If this is the last Session, continue to session_end
            return reverse('proposals:session_end', args=(self.object.study.pk,))

    def get_back_url(self):
        return reverse('proposals:task_update', args=(self.object.last_task().pk,))
