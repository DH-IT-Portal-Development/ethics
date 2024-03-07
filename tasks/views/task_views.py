# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, DeleteView, CreateView
from ..forms import TaskForm
from ..models import Task, Session


######################
# CRUD actions on Task
######################

class TaskMixin(AllowErrorsOnBackbuttonMixin):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_update.html"
    success_message = _("Taak bewerkt")

    def get_next_url(self):
        return reverse("tasks:session_end", args=(self.object.session.pk,))

    def get_back_url(self):
        return reverse("tasks:session_end", args=(self.object.session.pk,))

class TaskCreate(TaskMixin, CreateView):
    
    def form_valid(self, form):
        """Saves the Proposal on the WMO instance"""
        session = self.get_session()
        form.instance.session = session
        form.instance.order = session.task_set.count() + 1
        return super(TaskCreate, self).form_valid(form)

    def get_session(self):
        """Retrieves the Study from the pk kwarg"""
        return Session.objects.get(pk=self.kwargs["pk"])

class TaskUpdate(TaskMixin, AllowErrorsOnBackbuttonMixin, UpdateView):
    pass

class TaskDelete(DeleteView):
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
