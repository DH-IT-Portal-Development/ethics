# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, DeleteView
from ..forms import TaskForm
from ..mixins import DeletionAllowedMixin
from ..models import Task
from ..utils import get_task_progress


######################
# CRUD actions on Task
######################
class TaskUpdate(AllowErrorsOnBackbuttonMixin, UpdateView):
    """Updates a Task"""

    model = Task
    form_class = TaskForm
    success_message = _("Taak bewerkt")

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        context["progress"] = get_task_progress(self.object)
        return context

    def get_next_url(self):
        try:
            # Try to continue to next Task
            next_task = Task.objects.get(
                session=self.object.session, order=self.object.order + 1
            )
            return reverse("tasks:update", args=(next_task.pk,))
        except Task.DoesNotExist:
            # If this is the last Task, continue to task_end
            return reverse("tasks:end", args=(self.object.session.pk,))

    def get_back_url(self):
        try:
            # Try to return to previous Task
            prev_task = Task.objects.get(
                session=self.object.session, order=self.object.order - 1
            )
            return reverse("tasks:update", args=(prev_task.pk,))
        except Task.DoesNotExist:
            # If this is the first Task, return to task_start
            return reverse("tasks:start", args=(self.object.session.pk,))


class TaskDelete(DeletionAllowedMixin, DeleteView):
    """Deletes a Task"""

    model = Task
    success_message = _("Taak verwijderd")

    def get_success_url(self):
        return reverse("tasks:end", args=(self.object.session.pk,))

    def delete(self, request, *args, **kwargs):
        """
        Deletes the Task and updates the Session.
        Completely overrides the default delete function (as that calls delete too late for us).
        """
        self.object = self.get_object()
        order = self.object.order
        session = self.object.session
        success_url = self.get_success_url()
        self.object.delete()

        # If the order is lower than the total number of Tasks (e.g. 3 of 4), set the other orders one lower
        for t in Task.objects.filter(session=session, order__gt=order):
            t.order -= 1
            t.save()

        # Set the number of Tasks on Session
        session.tasks_number -= 1
        session.save()

        return HttpResponseRedirect(success_url)
