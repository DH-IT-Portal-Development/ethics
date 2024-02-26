# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, DeleteView
from ..forms import TaskForm
from ..mixins import DeletionAllowedMixin
from ..models import Task, Session

from cdh.core.views import RedirectActionView


######################
# CRUD actions on Task
######################


class TaskCreate(RedirectActionView):
    """Creates a task, from a session pk and redirects to TaskUpdate()
    for that task."""

    def action(self, request):
        session = Session.objects.get(pk=self.kwargs["pk"])
        order = session.task_set.count() + 1
        self.task = Task.objects.create(order=order, session=session)

    def get_redirect_url(self, *args, **kwargs):
        super().get_redirect_url(*args, **kwargs)
        return reverse("tasks:update", args=[self.task.pk])


class TaskUpdate(AllowErrorsOnBackbuttonMixin, UpdateView):
    """Updates a Task"""

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_update.html"
    success_message = _("Taak bewerkt")

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        if "create_new_task" in self.request.POST:
            return reverse("tasks:create", args=(self.object.session.pk,))
        else:
            return super().get_success_url()

    def get_next_url(self):
        return reverse("tasks:session_end", args=(self.object.session.pk,))

    def get_back_url(self):
        return reverse("tasks:session_update", args=(self.object.session.pk,))


class TaskDelete(DeletionAllowedMixin, DeleteView):
    """Deletes a Task"""

    model = Task
    success_message = _("Taak verwijderd")

    def get_success_url(self):
        return reverse("tasks:session_end", args=(self.object.session.pk,))

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

        return HttpResponseRedirect(success_url)
