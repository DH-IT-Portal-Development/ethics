# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, FormSetUpdateView
from proposals.mixins import ProposalContextMixin
from studies.models import Documents, Study
from studies.forms import StudyConsentForm
from studies.utils import create_documents_for_study
from ..forms import StudyStartForm
from ..models import Proposal


class StudyStart(
    ProposalContextMixin,
    AllowErrorsOnBackbuttonMixin,
    UpdateView,
):
    model = Proposal
    form_class = StudyStartForm
    template_name = "proposals/study_start.html"

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(StudyStart, self).get_form_kwargs()
        kwargs["proposal"] = self.object
        return kwargs

    def form_valid(self, form):
        """Creates or deletes Studies on save"""
        proposal = form.instance
        current = proposal.study_set.count() or 0
        if proposal.studies_similar:
            proposal.studies_number = 1

        # Create or update Studies
        for n in range(proposal.studies_number):
            order = n + 1
            s, _ = Study.objects.get_or_create(proposal=proposal, order=order)
            s.name = self.request.POST.get("study_name_" + str(order))
            s.save()

        # Delete Studies
        for n in range(proposal.studies_number, current):
            order = n + 1
            study = Study.objects.get(proposal=proposal, order=order)
            study.delete()

        return super(StudyStart, self).form_valid(form)

    def get_next_url(self):
        """Continue to the first Study"""
        proposal = self.object
        return reverse("studies:update", args=(proposal.first_study().pk,))

    def get_back_url(self):
        """Return to the Wmo overview"""
        return reverse("proposals:wmo_update", args=(self.object.wmo.pk,))
