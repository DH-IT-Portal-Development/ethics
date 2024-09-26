# -*- encoding: utf-8 -*-

from typing import Any
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, DeleteView, CreateView
from ..forms import TaskForm
from ..models import Task, Session
from proposals.mixins import StepperContextMixin


######################
# CRUD actions on Task
######################


class TaskMixin(
    StepperContextMixin,
    AllowErrorsOnBackbuttonMixin,
):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_update.html"
    success_message = _("Taak bewerkt")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session()
        context["session"] = session
        context["proposal"] = self.get_proposal()
        try:
            context["order"] = self.object.order
        except AttributeError:
            context["order"] = session.task_set.count() + 1
        context["session_order"] = session.order
        context["study_order"] = session.study.order
        context["study_name"] = session.study.name
        context["studies_number"] = session.study.proposal.studies_number
        return context

    def get_session(self):
        return self.get_object().session

    def get_proposal(self):
        return self.get_object().session.study.proposal

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
    
    def get_proposal(self):
        return self.get_session().study.proposal


class TaskUpdate(TaskMixin, UpdateView):
    pass


class TaskDelete(DeleteView):
    """Deletes a Task"""

    model = Task
    success_message = _("Taak verwijderd")

    def get_success_url(self):
        return reverse("tasks:session_end", args=(self.object.session.pk,))

    def form_valid(self, form):
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
