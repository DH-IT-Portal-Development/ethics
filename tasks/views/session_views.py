# -*- encoding: utf-8 -*-

from typing import Any
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, DeleteView
from ..forms import SessionUpdateForm, SessionEndForm
from ..mixins import DeletionAllowedMixin
from ..models import Session, Task, Study
from ..utils import copy_task_to_session

from cdh.core.views import RedirectActionView


######################
# Actions on a Session
######################
class SessionDelete(DeletionAllowedMixin, DeleteView):
    model = Session
    success_message = _("Sessie verwijderd")

    def get_success_url(self):
        return reverse("studies:design_end", args=(self.object.study.pk,))

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

        return HttpResponseRedirect(success_url)


##################
# Actions on Sessions
##################


class SessionCreate(RedirectActionView):
    """Creates a session, from a study pk and redirects to SessionUpdate()
    for that session."""

    def action(self, request):
        study = Study.objects.get(pk=self.kwargs["pk"])
        order = study.session_set.count() + 1
        self.session = Session.objects.create(order=order, study=study)

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str | None:
        super().get_redirect_url(*args, **kwargs)
        return reverse("tasks:session_update", args=[self.session.pk])


class SessionUpdate(AllowErrorsOnBackbuttonMixin, UpdateView):
    """Initial creation of Tasks for a Session"""

    model = Session
    form_class = SessionUpdateForm
    template_name = "tasks/task_start.html"

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(SessionUpdate, self).get_form_kwargs()
        kwargs["study"] = self.object.study
        return kwargs

    def get_next_url(self):
        tasks = self.object.task_set.all()
        if tasks.count() == 0:
            return reverse("tasks:create", args=(self.object.pk,))
        else:
            return reverse("tasks:update", args=(tasks.get(order=1).pk,))

    def get_back_url(self):
        try:
            # Try to return to session_end of the previous Session
            prev_session = Session.objects.get(
                study=self.object.study, order=self.object.order - 1
            )
            return reverse("tasks:session_end", args=(prev_session.pk,))
        except Session.DoesNotExist:
            study = self.object.study
            next_url = "studies:design"
            pk = study.pk
            if study.has_observation:
                next_url = "observations:update"
                pk = study.observation.pk
            elif study.has_intervention:
                next_url = "interventions:update"
                pk = study.intervention.pk
            return reverse(next_url, args=(pk,))


class SessionEnd(AllowErrorsOnBackbuttonMixin, UpdateView):
    """Completes a Session"""

    model = Session
    form_class = SessionEndForm
    template_name = "tasks/task_end.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        referrer = self.request.META.get("HTTP_REFERRER")
        if referrer:
            pass

        return kwargs

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        if "create_new_session" in self.request.POST:
            return reverse("tasks:session_create", args=(self.object.study.pk,))
        else:
            return super().get_success_url()

    def get_next_url(self):
        try:
            # Try to continue to next Session
            next_session = Session.objects.get(
                study=self.object.study, order=self.object.order + 1
            )
            return reverse("tasks:session_update", args=(next_session.pk,))
        except Session.DoesNotExist:
            # If this is the last Session, continue to design_end
            return reverse("studies:design_end", args=(self.object.study.pk,))

    def get_back_url(self):
        return reverse("tasks:update", args=(self.object.last_task().pk,))
