# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from .base_views import UpdateView, DeleteView, get_task_progress
from ..forms import TaskForm
from ..mixins import AllowErrorsMixin
from ..models import Task


######################
# CRUD actions on Task
######################
class TaskUpdate(AllowErrorsMixin, UpdateView):
    """Updates a Task"""
    model = Task
    form_class = TaskForm
    success_message = _('Taak bewerkt')

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        context['progress'] = get_task_progress(self.object)
        return context

    def get_next_url(self):
        try:
            # Try to continue to next Task
            next_task = Task.objects.get(session=self.object.session, order=self.object.order + 1)
            return reverse('proposals:task_update', args=(next_task.id,))
        except Task.DoesNotExist:
            # If this is the last Task, continue to task_end
            return reverse('proposals:task_end', args=(self.object.session.id,))

    def get_back_url(self):
        try:
            # Try to return to previous Task
            prev_task = Task.objects.get(session=self.object.session, order=self.object.order - 1)
            return reverse('proposals:task_update', args=(prev_task.id,))
        except Task.DoesNotExist:
            # If this is the first Task, return to task_start
            return reverse('proposals:task_start', args=(self.object.session.id,))


class TaskDelete(DeleteView):
    """Deletes a Task"""
    model = Task
    success_message = _('Taak verwijderd')

    def get_success_url(self):
        # TODO: fix task order just like sessions above
        return reverse('proposals:detail', args=(self.object.session.proposal.id,))