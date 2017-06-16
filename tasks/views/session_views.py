# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from core.views import AllowErrorsMixin, UpdateView, DeleteView
from ..forms import TaskStartForm, TaskEndForm
from ..mixins import DeletionAllowedMixin
from ..models import Session, Task
from ..utils import copy_task_to_session, get_session_progress


######################
# Actions on a Session
######################
class SessionDelete(DeletionAllowedMixin, DeleteView):
    model = Session
    success_message = _('Sessie verwijderd')

    def get_success_url(self):
        return reverse('studies:design_end', args=(self.object.study.pk,))

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


##################
# Actions on Tasks
##################
class TaskStart(AllowErrorsMixin, UpdateView):
    """Initial creation of Tasks for a Session"""
    model = Session
    form_class = TaskStartForm
    template_name = 'tasks/task_start.html'
    success_message = _('%(tasks_number)s ta(a)k(en) aangemaakt')

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(TaskStart, self).get_form_kwargs()
        kwargs['study'] = self.object.study
        return kwargs

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
            for task in s.task_set.all():
                copy_task_to_session(session, task)
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

            # If the number of Tasks has changed, invalidate the Session duration
            if current != nr_tasks:
                session.tasks_duration = None
                session.save()

        return super(TaskStart, self).form_valid(form)

    def get_next_url(self):
        return reverse('tasks:update', args=(self.object.first_task().pk,))

    def get_back_url(self):
        try:
            # Try to return to task_end of the previous Session
            prev_session = Session.objects.get(study=self.object.study, order=self.object.order - 1)
            return reverse('tasks:end', args=(prev_session.pk,))
        except Session.DoesNotExist:
            # If this is the first Session, return to session_start
            return reverse('studies:session_start', args=(self.object.study.pk,))


class TaskEnd(AllowErrorsMixin, UpdateView):
    """Completes a Session"""
    model = Session
    form_class = TaskEndForm
    template_name = 'tasks/task_end.html'
    success_message = _(u'Taken toevoegen beëindigd')

    def get_context_data(self, **kwargs):
        context = super(TaskEnd, self).get_context_data(**kwargs)
        context['progress'] = get_session_progress(self.object, True)
        return context

    def get_next_url(self):
        try:
            # Try to continue to next Session
            next_session = Session.objects.get(study=self.object.study, order=self.object.order + 1)
            return reverse('tasks:start', args=(next_session.pk,))
        except Session.DoesNotExist:
            # If this is the last Session, continue to design_end
            return reverse('studies:design_end', args=(self.object.study.pk,))

    def get_back_url(self):
        return reverse('tasks:update', args=(self.object.last_task().pk,))
