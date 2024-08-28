# -*- encoding: utf-8 -*-

from typing import Any
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, DeleteView, CreateView
from proposals.mixins import StepperContextMixin
from studies.mixins import StudyFromURLMixin, StudyMixin
from ..forms import SessionUpdateForm, SessionEndForm, SessionOverviewForm
from ..models import Session, Study


######################
# Actions on a Session
######################
class SessionDelete(DeleteView):
    model = Session
    success_message = _("Sessie verwijderd")

    def get_success_url(self):
        return reverse("tasks:session_overview", args=(self.object.study.pk,))

    def form_valid(self, form):
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


class SessionMixin(
        StepperContextMixin,
        AllowErrorsOnBackbuttonMixin,
):

    model = Session
    form_class = SessionUpdateForm
    template_name = "tasks/session_update.html"

    def get_context_data(self, **kwargs):
        study = self.get_study()
        context = super().get_context_data(**kwargs)
        context["study"] = study
        context["proposal"] = study.proposal
        return context

    def get_study(self):
        return self.object.study

    def get_next_url(self):
        return reverse("tasks:session_end", args=(self.object.pk,))

    def get_proposal(self,):
        return self.get_object().study.proposal


class SessionStart(SessionMixin, UpdateView):

    model = Study
    # This form is just a placeholder to make navigation work. It does not do
    # anything.
    form_class = SessionOverviewForm
    template_name = "tasks/session_start.html"

    def get_next_url(self):
        return reverse("tasks:session_overview", args=(self.object.pk,))

    def get_back_url(self):
        study = self.object
        next_url = "studies:design"
        pk = study.pk
        if study.has_observation:
            next_url = "observations:update"
            pk = study.observation.pk
        elif study.has_intervention:
            next_url = "interventions:update"
            pk = study.intervention.pk
        return reverse(next_url, args=(pk,))

    def get_study(self):
        return self.object

    def get_proposal(self,):
        return self.get_object().proposal


class SessionCreate(
        StudyFromURLMixin,
        SessionMixin,
        CreateView,
):

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(SessionCreate, self).get_form_kwargs()
        kwargs["study"] = self.get_study()
        return kwargs

    def form_valid(self, form):
        """Saves the Proposal on the WMO instance"""
        study = self.get_study()
        form.instance.study = study
        form.instance.order = study.session_set.count() + 1
        return super(SessionCreate, self).form_valid(form)

    def get_back_url(self):
        return reverse("tasks:session_overview", args=(self.object.study.pk,))


class SessionUpdate(SessionMixin, UpdateView):

    def get_form_kwargs(self):
        """Sets the Study as a form kwarg"""
        kwargs = super(SessionUpdate, self).get_form_kwargs()
        kwargs["study"] = self.object.study
        return kwargs

    def get_back_url(self):
        return reverse("tasks:session_end", args=(self.object.study.pk,))


class SessionEnd(SessionMixin, UpdateView):
    """Completes a Session"""

    form_class = SessionEndForm
    template_name = "tasks/session_end.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_edit_tasks"] = True
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        referrer = self.request.META.get("HTTP_REFERRER")
        if referrer:
            pass

        return kwargs

    def get_next_url(self):
        return reverse("tasks:session_overview", args=(self.object.study.pk,))

    def get_back_url(self):
        return reverse("tasks:session_overview", args=(self.object.study.pk,))


class SessionOverview(StudyMixin, UpdateView):

    model = Study
    form_class = SessionOverviewForm
    template_name = "tasks/session_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_edit_sessions"] = True
        context["proposal"] = self.object.proposal
        return context

    def get_next_url(self):
        return reverse("studies:design_end", args=(self.object.pk,))

    def get_back_url(self):
        return reverse("tasks:session_start", args=(self.object.pk,))
